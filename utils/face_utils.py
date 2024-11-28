import os
import time
from deepface import DeepFace
import cv2
from werkzeug.utils import secure_filename
import numpy as np
from config import DETECTIONS_FOLDER
from redis.commands.search.query import Query
from utils.redis_utils import redis_db, redis_client
from utils.db_utils import initialize_db
from models import db, DetectionRecords
import json

os.environ["CUDA_VISIBLE_DEVICES"] = "0" 
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

initialize_db()

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


def make_query_vector(face):
    face_path = face['face_path']
        
    target_embedding = DeepFace.represent(
        img_path=face_path,
        model_name="ArcFace",
        enforce_detection=False, 
        detector_backend="skip"  
    )[0]["embedding"]

    query_vector = np.array(target_embedding).astype(np.float32).tobytes()
    
    result = {
        "face_vector": query_vector,
    }
    
    return result


def get_nearest_neighbors(query_vector, k):
    base_query = f"*=>[KNN {k} @embedding $query_vector AS distance]"
    query = Query(base_query).return_fields("distance").sort_by("distance").dialect(2)
    results = redis_db.ft().search(query, query_params={"query_vector": query_vector})

    return results


def identity_max_accuracies(max_conf_dict, nearest_neighbors, face_id, detection_id):
    if nearest_neighbors and nearest_neighbors.docs:
        identity = nearest_neighbors.docs[0].id
        distance = round(float(nearest_neighbors.docs[0].distance), 2)
        confidence = round((100 - distance), 2)

        max_conf_dict[identity] = max(max_conf_dict.get(identity, 0), confidence)
            
        return {"detection_id": detection_id, "detected": face_id, "identity": identity, "confidence": confidence}
    else:
        return {"detection_id": detection_id, "detected": face_id, "identity": None, "confidence": 0}


def save_captured_frames(captured_frames, captures_folder):
    captured_frames_list = []
    
    for captured_frame in captured_frames:
        filename = secure_filename(captured_frame.filename)
        captured_path = os.path.join(captures_folder, filename)
        captured_frame.save(captured_path)

        captured_frames_list.append({"path": captured_path, "filename": filename})
    
    return captured_frames_list


def crop_faces(location_id, all_faces_list, datetime_obj):
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
        cropped_face_img_path = os.path.join(DETECTIONS_FOLDER, new_face_id)
        cv2.imwrite(cropped_face_img_path, face_img)
        
        # Save detected on DB
        new_detection = DetectionRecords(
            status_id = 1, # ---> 1 - Detected
            datetime = datetime_obj,
            confidence = 0,
            origin_path = origin_path,
            detected_path = cropped_face_img_path,
            location_id = location_id,
        )
        db.session.add(new_detection)
        db.session.commit()

        detection_dict = {
            "id": new_detection.id,
            "status": new_detection.status.status,
            "location_id": location_id
        }

        redis_client.publish("detection_events", json.dumps(detection_dict))

        cropped_faces_list.append({"detection_id": new_detection.id , "face_path": cropped_face_img_path, "face_id": new_face_id})
        
    return cropped_faces_list