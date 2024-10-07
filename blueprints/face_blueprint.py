from flask import Response, request, send_from_directory, abort, jsonify, Blueprint, current_app
from celery.result import AsyncResult
from datetime import datetime
import cv2
import os
import json
from werkzeug.utils import secure_filename
from config import CAPTURES_FOLDER, DETECTIONS_FOLDER, FACE_DATABASE
from utils import NumpyArrayEncoder
from face_utils import save_captured_frames
from face_tasks import recognize_faces, detect_faces
from redis_con import init_redis


face_blueprint = Blueprint('face', __name__)

@face_blueprint.route('/recognize-faces', methods=['POST'])
def recognize_faces_route():
    print("Recognizing face...")

    # Get faces and captured_path from request
    data = request.get_json()
    faces = data.get('faces')['faces']
    datetime_str = data.get('datetime')
    
    date_object = datetime.strptime(datetime_str, '%B %d, %Y at %I:%M:%S %p') # Sample: September 21, 2024 at 10:30:45 PM
    print(f'Faces detected on: {date_object}')
    
    job = recognize_faces.apply_async(args=[faces, datetime_str, FACE_DATABASE], queue='recognition')
    return jsonify({'job_id': job.id}), 201


@face_blueprint.route('/detect-faces', methods=['POST'])
def detect_faces_route():
    print("Detecting faces...")
    
    # Check if 'capturedFrame' was sent from request
    if 'capturedFrames' not in request.files:
        return jsonify({'error': 'No capturedFrames part'}), 400
    
    captured_frames = request.files.getlist('capturedFrames')
    
    captured_frames_list = save_captured_frames(captured_frames, CAPTURES_FOLDER)
    
    # Temporary location id = 1
    job = detect_faces.apply_async(args=[captured_frames_list, 1], queue='detection')
    return jsonify({'job_id': job.id}), 201


@face_blueprint.route('/recognized-face/<filename>')
def recognized_face(filename):
    file_path = os.path.join(FACE_DATABASE, filename)
    
    if os.path.exists(file_path):
        return send_from_directory(directory=FACE_DATABASE, path=filename)
    else:
        abort(404)


@face_blueprint.route('/detected-face/<filename>')
def detected_face(filename):
    file_path = os.path.join(DETECTIONS_FOLDER, filename)
    
    if os.path.exists(file_path):
        return send_from_directory(directory=DETECTIONS_FOLDER, path=filename)
    else:
        abort(404)


@face_blueprint.route('/capture', methods=['POST'])
def capture():
    print("Capturing frame...")
    global cam
    ret, frame = cam.read()

    if not ret:
        return "Failed to capture image."
    
    if frame is not None:
        filename = f"{datetime.now().timestamp()}.jpg"
        cv2.imwrite(os.path.join("static", filename), frame)
        
    json_data = json.dumps({"capturedPath": filename}, cls=NumpyArrayEncoder)
    
    return Response(json_data, mimetype='application/json')



@face_blueprint.route('/detections/<int:location_id>', methods=['POST', 'GET'])
def detections_event_stream(location_id):
    redis_client = init_redis(current_app)
    def event_stream():
        channel_name = f'detection_results_{location_id}'
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel_name)
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                yield 'data: %s\n\n' % json.dumps(message['data'])
    
    return Response(event_stream(), mimetype="text/event-stream")


@face_blueprint.route('/task-result/<job_id>', methods=['POST', 'GET'])
def get_task_result(job_id):
    task = AsyncResult(job_id)
    
    if task.state == 'PENDING':
        return jsonify({'state': 'PENDING', 'status': 'Task is waiting...'}), 200
    
    elif task.state != 'FAILURE':
        result = task.result
        
        return jsonify({'state': task.state, 'result': result}), 200 #SUCCESS
    
    else:
        return jsonify({'state': task.state, 'status': str(task.info)}), 500 #FAIL

