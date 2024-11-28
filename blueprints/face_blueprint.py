from flask import Response, request, send_from_directory, abort, jsonify, Blueprint, current_app, stream_with_context
from celery.result import AsyncResult
from celery import chain
from datetime import datetime
import os
import json
import pytz
import time
from config import CAPTURES_FOLDER, DETECTIONS_FOLDER, FACE_DATABASE
from utils.utils import NumpyArrayEncoder
from utils.face_utils import save_captured_frames
from tasks.face_tasks import recognize_faces, detect_faces
from utils.redis_utils import redis_client
from urllib.parse import unquote
from models import DetectionRecords

face_blueprint = Blueprint('face', __name__)

@face_blueprint.route('/events', methods=['GET'])
def sse_events():
    def stream():
        pubsub = redis_client.pubsub()
        pubsub.subscribe("detection_events")

        pubsub.psubscribe("__keyevent@0__:expired")
        
        timeout = 1 
        last_event_time = time.time()

        while True:
            message = pubsub.get_message(timeout=timeout)
            current_time = time.time()

            if current_time - last_event_time >= 10:
                yield ":\n\n"  # Comment line for keep-alive
                last_event_time = current_time

            if message and message['type'] == 'message':  # Ignore other message types
                yield f"data: {message['data']}\n\n"
                last_event_time = current_time

            # Prevent CPU overutilization
            time.sleep(0.01)

    response = Response(
        stream_with_context(stream()),
        content_type="text/event-stream"
    )

    return response


@face_blueprint.route('/recognize-faces', methods=['POST'])
def recognize_faces_route():
    print("Detecting then recognizing faces...")

    if 'datetime' not in request.form or 'capturedFrames' not in request.files:
        return jsonify({'error': 'Invalid input'}), 400
    
    captured_frames = request.files.getlist('capturedFrames')
    captured_frames_list = save_captured_frames(captured_frames, CAPTURES_FOLDER)

    location_id = request.form.get('location_id')
    group_id = request.form.get('group_id')

    datetime_iso = request.form.get('datetime')
    datetime_obj = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))
    
    local_timezone = pytz.timezone('Asia/Manila')
    local_datetime = datetime_obj.astimezone(local_timezone)

    detect_faces_task = detect_faces.s(location_id, captured_frames_list, local_datetime).set(queue='detection')
    recognize_faces_task = recognize_faces.s(location_id=location_id, group_id=group_id).set(queue='recognition')

    job = chain(detect_faces_task, recognize_faces_task).apply_async()
    return jsonify({'job_id': job.id}), 201



@face_blueprint.route('/detection-record/<int:detection_id>', methods=['GET'])
def detection_record(detection_id):
    detection = DetectionRecords.query.filter_by(id=detection_id).first()

    if not detection:
        return jsonify({'error': 'Detection record does not exist'}), 404

    detection_dict = {
        "id": detection.id,
        "datetime": detection.datetime,
        "confidence": detection.confidence,
        "origin_path": detection.origin_path,
        "detected_path": detection.detected_path,
        "detected_name": detection.user.user_info.full_name if detection.user and detection.user.user_info else "",
        "status": detection.status.status,
        "type": detection.type.type_name if detection.type else None,
        "image": detection.user.identity_image if detection.user and detection.user.has_identity else None
    }
    
    return jsonify({'detection': detection_dict}), 200


@face_blueprint.route('/detected-face/<path:filepath>')
def detected_face(filepath):
    decoded_path = unquote(filepath)
    if os.path.exists(decoded_path):
        return send_from_directory(directory=os.path.dirname(decoded_path), path=os.path.basename(decoded_path))
    abort(404)


@face_blueprint.route('/task-result/<job_id>', methods=['POST', 'GET'])
def get_task_result(job_id):
    task = AsyncResult(job_id)
    
    if task.state == 'PENDING':
        json_data = json.dumps({'state': 'PENDING', 'status': 'Task is waiting...'}, cls=NumpyArrayEncoder)
        return Response(json_data, mimetype='application/json'), 200 # pending
    
    elif task.state != 'FAILURE':
        result = task.result
        json_data = json.dumps({'state': task.state, 'result': result}, cls=NumpyArrayEncoder)
        return Response(json_data, mimetype='application/json'), 200 # success
    
    else:
        json_data = json.dumps({'state': task.state, 'status': str(task.info)}, cls=NumpyArrayEncoder)
        return Response(json_data, mimetype='application/json'), 500 # fail

