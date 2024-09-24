import os
import time
import json
from flask import Response
from datetime import datetime
from deepface import DeepFace
from retinaface import RetinaFace
import cv2
from werkzeug.utils import secure_filename
from config import CAPTURES_FOLDER, DETECTIONS_FOLDER, FACE_DATABASE
from utils import NumpyArrayEncoder

def recognize_faces(faces, datetime_str, face_database_path):
    results = []
    max_accuracies = {} # temp holder for max accuracy of each detected indentity
    
    for face in faces:
        recognition_result = use_recognition_model(face, face_database_path)
        face_id = recognition_result["face_id"]
        filtered_result = recognition_result["filtered_result"]
        id_max_accuracy = identity_max_accuracies(max_accuracies, filtered_result, face_id, datetime_str)
        results.append(id_max_accuracy) 
    
    # Update identities based on maximum accuracies
    for result in results:
        if result['identity'] and result['accuracy'] < max_accuracies[result['identity']]:
            result['identity'] = None
            result['accuracy'] = 0
    
    return results


def use_recognition_model(face, face_database_path):
    face_path = face['face_path']
    face_id = face['face_id']
        
    result = DeepFace.find(
        img_path=face_path, 
        db_path=face_database_path,
        model_name="ArcFace",
        detector_backend="retinaface",
        enforce_detection=False,
    )
    
    recognition_result = {
        "face_id": face_id,
        "filtered_result": [df for df in result if not df.empty],
    }
    
    return recognition_result


def identity_max_accuracies(max_acc_dict, filtered_result, face_id, datetime_str):
    if filtered_result:
        sorted_result = sorted(filtered_result, key=lambda df: df.iloc[0]['distance'])
        identity = sorted_result[0].iloc[0]['identity']
        accuracy = (1 - sorted_result[0].iloc[0]['distance']) * 100
            
        # If identity is in max_accuracies, compare accuracies, and replace max
        max_acc_dict[identity] = max(max_acc_dict.get(identity, 0), accuracy)
            
        return {"detected": face_id, "identity": identity, "accuracy": accuracy, "datetime": datetime_str}
    else:
        return {"detected": face_id, "identity": None, "accuracy": 0, "datetime": datetime_str}


def detect_faces(captured_files, captures_folder):
    all_faces_list = []
    
    for captured_file in captured_files:
        filename = secure_filename(captured_file.filename)
        captured_path = os.path.join(captures_folder, filename)
        captured_file.save(captured_path)

        frame = cv2.imread(captured_path)
        faces = RetinaFace.detect_faces(frame)
        faces_list = [{"face_id": str(face_id), "face_info": face_info, "origin_path": captured_path, "origin_filename": filename} 
                        for face_id, face_info in faces.items()]
        
        all_faces_list.extend(faces_list)
        
    cropped_faces_list = crop_faces(all_faces_list, DETECTIONS_FOLDER)
        
    return cropped_faces_list


def crop_faces(all_faces_list, detections_folder):
    cropped_faces_list = []
    
    for face in all_faces_list:
        face_id = face['face_id']
        face_info = face['face_info']
        origin_path = face['origin_path']
        origin_filename = face['origin_filename']
        facial_area = face_info.get('facial_area', [0, 0, 0, 0])
        
        frame = cv2.imread(origin_path)
        face_img = frame[facial_area[1]:facial_area[3], facial_area[0]:facial_area[2]]
            
        new_face_id = f"{face_id}({origin_filename})-{int(time.time())}.jpg"
        cropped_face_img_path = os.path.join(detections_folder, new_face_id)
        cv2.imwrite(cropped_face_img_path, face_img)
        
        cropped_faces_list.append({"face_path": cropped_face_img_path, "face_id": new_face_id})
        
    return cropped_faces_list