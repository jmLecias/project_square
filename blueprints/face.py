from flask import Response, request, send_from_directory, abort, jsonify, Blueprint
from flask_cors import CORS
from deepface import DeepFace
from retinaface import RetinaFace
from datetime import datetime
import time
import cv2
import os
import json
from werkzeug.utils import secure_filename
from config import CAPTURES_FOLDER, DETECTIONS_FOLDER, FACE_DATABASE
from utils import NumpyArrayEncoder
from face_utils import recognize_faces, detect_faces

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
    
    results = recognize_faces(faces, datetime_str, FACE_DATABASE)
    print(results)
    
    json_data = json.dumps({"results": results}, cls=NumpyArrayEncoder)
    
    return Response(json_data, mimetype='application/json')
        

@face_blueprint.route('/detect-faces', methods=['POST'])
def detect_faces_route():
    print("Detecting faces...")
    
    # Check if 'capturedFrame' was sent from request
    if 'capturedFrames' not in request.files:
        return jsonify({'error': 'No capturedFrames part'}), 400
    
    cropped_faces_list = detect_faces(request.files.getlist('capturedFrames'), CAPTURES_FOLDER)
    
    json_data = json.dumps({"faces": cropped_faces_list}, cls=NumpyArrayEncoder)
    return Response(json_data, mimetype='application/json')


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