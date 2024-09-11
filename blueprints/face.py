from flask import Flask, render_template, Response, request, send_from_directory, abort, jsonify, Blueprint
from flask_cors import CORS
from deepface import DeepFace
from retinaface import RetinaFace
from datetime import datetime
import time
import cv2
import numpy as np
import pandas as pd
import os
import shutil
import json
from werkzeug.utils import secure_filename

face_blueprint = Blueprint('face', __name__)

UPLOAD_FOLDER = 'uploads'
CAPTURES_FOLDER = 'uploads/captures'
DETECTIONS_FOLDER = 'faces/detections'
FACE_DATABASE = 'faces/database/class1'

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)
        

@face_blueprint.route('/recognize-faces', methods=['POST'])
def recognize_faces():
    print("Recognizing face...")
    results = []

    # Get faces and captured_path from request
    data = request.get_json()
    faces = data.get('faces')
    
    # Remake the 'faces/detections' folder if not exists
    if not os.path.exists(DETECTIONS_FOLDER):
        os.makedirs(DETECTIONS_FOLDER)
    
    # Loop through every face from detections, crop them using 'facial_area'
    # Save each detected face temporarily in 'faces/detections'
    for face in faces:
        face_id = face['face_id']
        face_info = face['face_info']
        origin = face['origin']
        facial_area = face_info.get('facial_area', [0, 0, 0, 0])
        
        frame = cv2.imread(origin)
        face_img = frame[facial_area[1]:facial_area[3], facial_area[0]:facial_area[2]]
            
        new_face_id = f"{face_id}-{int(time.time())}.jpg"
        temp_face_img_path = os.path.join(DETECTIONS_FOLDER, new_face_id)
        cv2.imwrite(temp_face_img_path, face_img)
            
        result = DeepFace.find(
            img_path=temp_face_img_path, 
            db_path=FACE_DATABASE,
            model_name="ArcFace",
            detector_backend="retinaface",
            enforce_detection=False,
        )
            
        filtered_result = [df for df in result if not df.empty]
            
        if filtered_result:
            sorted_result = sorted(filtered_result, key=lambda df: df.iloc[0]['distance'])
            identity = sorted_result[0].iloc[0]['identity']
            accuracy = (1 - sorted_result[0].iloc[0]['distance']) * 100
            results.append({"detected": new_face_id, "identity": identity, "accuracy": accuracy})
        else:
            results.append({"detected": new_face_id, "identity": None, "accuracy": 0})
            print(f"Face {face_id} does not have any matches in face database.")
    
    max_accuracies = {}
    for result in results:
        identity = result['identity']
        accuracy = result['accuracy']
        if identity not in max_accuracies or accuracy > max_accuracies[identity]:
            max_accuracies[identity] = accuracy
            
    for result in results:
        if result['accuracy'] < max_accuracies[result['identity']]:
            result['identity'] = None
            result['accuracy'] = 0
        
    print(results)
    
    json_data = json.dumps({"results": results}, cls=NumpyArrayEncoder)
    
    return Response(json_data, mimetype='application/json')
        

@face_blueprint.route('/detect-faces', methods=['POST'])
def detect_faces():
    print("Detecting faces...")
    
    # Check if 'capturedFrame' was sent from request
    if 'capturedFrames' not in request.files:
        return jsonify({'error': 'No capturedFrames part'}), 400
    
    # Delete previous face detections, if there is any
    if os.path.exists(DETECTIONS_FOLDER):
        shutil.rmtree(DETECTIONS_FOLDER)
        
    all_faces_list = []
    
    # If exists, check for its filename
    for captured_file in request.files.getlist('capturedFrames'):
        if captured_file.filename == '':
            return jsonify({'error': 'No selected image'}), 400
    
        # Clean the filename, then save to 'uploads/captures'
        filename = secure_filename(captured_file.filename)
        captured_path = os.path.join(CAPTURES_FOLDER, filename)
        captured_file.save(captured_path)

        # Read save captured_file, detect faces, and save to list
        frame = cv2.imread(captured_path)
        faces = RetinaFace.detect_faces(frame)
        faces_list = [{"face_id": str(face_id), "face_info": face_info, "origin": captured_path} for face_id, face_info in faces.items()]
        
        # Append faces_list to all_faces_list
        all_faces_list.extend(faces_list)
        
    json_data = json.dumps({"faces": all_faces_list}, cls=NumpyArrayEncoder)
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