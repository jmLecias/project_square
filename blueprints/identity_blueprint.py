from flask import Response, request, send_from_directory, abort, jsonify, Blueprint, current_app
from celery.result import AsyncResult
from datetime import datetime
import cv2
import json
from werkzeug.utils import secure_filename
from utils.utils import NumpyArrayEncoder
from utils.face_utils import save_captured_frames
from tasks.identity_tasks import identity_upload, save_face_embeddings
from redis_con import init_redis
from config import TEMP_FOLDER
from werkzeug.utils import secure_filename
import os

identity_blueprint = Blueprint('identity', __name__)


@identity_blueprint.route('/upload', methods=['POST'])
def identity_upload_route():

    if 'faceImages' not in request.files:
        return jsonify({'error': 'No faceImages part'}), 400
    
    face_images = request.files.getlist('faceImages')
    first_name = request.form.get('first_name')
    middle_name = request.form.get('middle_name')
    last_name = request.form.get('last_name')
    user_id = request.form.get('user_id')

    os.makedirs(TEMP_FOLDER, exist_ok=True)

    face_image_paths = []
    for face_image in face_images:
        filename = secure_filename(face_image.filename)
        temp_file_path = os.path.join(TEMP_FOLDER, filename)
        face_image.save(temp_file_path)
        face_image_paths.append(temp_file_path)
    
    personal_info ={
        "firstname": first_name,
        "middlename": middle_name,
        "lastname": last_name,
    }
    
    job = identity_upload.apply_async(args=[face_image_paths, personal_info, user_id], queue='upload')

    return jsonify({'job_id': job.id}), 201


@identity_blueprint.route('/save-embeddings', methods=['POST'])
def save_face_embeddings_route():
    data = request.get_json()
    face_image_path = data.get('face_image_path')
    unique_key = data.get('unique_key')

    job = save_face_embeddings.apply_async(args=[face_image_path, unique_key], queue='upload')
    
    return jsonify({'job_id': job.id}), 200


@identity_blueprint.route('/upload-result/<job_id>', methods=['POST', 'GET'])
def get_upload_result(job_id):
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