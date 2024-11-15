from flask import Flask, current_app
from retinaface import RetinaFace
import cv2
import json
from celery import shared_task
from config import DETECTIONS_FOLDER
from utils.face_utils import *
from celery.exceptions import Ignore
from models import db, UserInfos, FaceImages

# Initialize Flask app context (without running the app)
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@192.168.254.102:3306/project_square'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@shared_task(bind=True)
def recognize_faces(self, faces, datetime_str):
    results = []
    max_accuracies = {} # temp holder for max accuracy of each detected identity
    face_results = {} # temp holder for knn results of each detected face
    
    for face in faces:
        query_vector = make_query_vector(face)
        face_id = query_vector["face_id"]
        
        face_vector = query_vector["face_vector"]
        nearest_neighbors = get_nearest_neighbors(face_vector, 2)
        
        face_results[face_id] = nearest_neighbors

        id_max_accuracy = identity_max_accuracies(max_accuracies, nearest_neighbors, face_id, datetime_str)
        results.append(id_max_accuracy) 
    
    # Update identities based on maximum accuracies
    for result in results:
        if result['identity'] and result['accuracy'] < max_accuracies[result['identity']]:
            result['identity'] = None
            result['accuracy'] = 0
    
    return results


@shared_task(bind=True)
def detect_faces(self, captured_frames_list):
    
    all_faces_list = []
    
    for captured_frame in captured_frames_list:
        captured_frame_path = captured_frame["path"]
        captured_frame_filename = captured_frame["filename"]
        
        frame = cv2.imread(captured_frame_path)
        faces = RetinaFace.detect_faces(frame)
        faces_list = [{"face_id": str(face_id), "face_info": face_info, "origin_path": captured_frame_path, "origin_filename": captured_frame_filename} 
                        for face_id, face_info in faces.items()]
        
        all_faces_list.extend(faces_list)
    
    cropped_faces_list = crop_faces(all_faces_list, DETECTIONS_FOLDER)
    
    return cropped_faces_list