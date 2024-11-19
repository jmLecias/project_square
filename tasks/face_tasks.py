from flask import Flask, current_app
from retinaface import RetinaFace
import cv2
import json
from celery import shared_task
from config import DETECTIONS_FOLDER
from models import db, DetectionRecords, FaceImages, Groups

from utils.face_utils import *
from utils.redis_utils import redis_db, redis_client
from utils.db_utils import initialize_db

initialize_db()

@shared_task(bind=True)
def recognize_faces(self, faces, location_id, group_id):
    results = []
    max_confidences = {} # temp holder for max accuracy of each detected identity
    face_results = {} # temp holder for knn results of each detected face
    
    for face in faces:
        detection_id = face["detection_id"]
        face_id = face["face_id"]

        query_vector = make_query_vector(face)
        face_vector = query_vector["face_vector"]
        nearest_neighbors = get_nearest_neighbors(face_vector, 2)
        
        face_results[face_id] = nearest_neighbors

        id_max_confidence = identity_max_accuracies(max_confidences, nearest_neighbors, face_id, detection_id)
        results.append(id_max_confidence) 
    
    # Update identities based on maximum accuracies
    for result in results:
        if result['identity'] and result['confidence'] < max_confidences[result['identity']]:
            result['identity'] = None
            result['confidence'] = 0

    for result in results:
        detection_id = result["detection_id"]
        confidence = result["confidence"]
        identity = result["identity"]

        face_image = FaceImages.query.filter_by(unique_key=identity).first()

        user = None
        if face_image:
            user = face_image.user
        elif not result["identity"] == None:
            redis_db.delete(identity)
            result["identity"] = None

            
        group = Groups.query.filter_by(id=group_id).first()

        detection_record = DetectionRecords.query.get(detection_id)

        # Update detection record
        if detection_record:
            detection_record.confidence = confidence

            if user and group.is_user_in_group(user.id):
                detection_record.status_id = 2  # Recognized
                detection_record.user_id = user.id
                detection_record.identity_key = identity
            else:
                detection_record.status_id = 3  # Unknown
                result["identity"] = None
        else:
            print(f"Detection record with ID {detection_id} not found.")

        # Commit the updates to the database
        db.session.commit()

        # update = {
        #     "detection_id": detection_id,
        #     "location_id": location_id
        # }

        detection_dict = {
            "id": detection_record.id,
            'status': detection_record.status.status,
            "location_id": location_id
        }

        redis_client.publish("detection_events", json.dumps(detection_dict))
        
    return results


@shared_task(bind=True)
def detect_faces(self, location_id, captured_frames_list, datetime):
    
    all_faces_list = []
    
    for captured_frame in captured_frames_list:
        captured_frame_path = captured_frame["path"]
        captured_frame_filename = captured_frame["filename"]
        
        frame = cv2.imread(captured_frame_path)
        faces = RetinaFace.detect_faces(frame)
        faces_list = [{"face_id": str(face_id), "face_info": face_info, "origin_path": captured_frame_path, "origin_filename": captured_frame_filename} 
                        for face_id, face_info in faces.items()]
        
        all_faces_list.extend(faces_list)
    
    cropped_faces_list = crop_faces(location_id, all_faces_list, datetime)
    
    return cropped_faces_list