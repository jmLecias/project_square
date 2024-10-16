import os
import time
from deepface import DeepFace
from retinaface import RetinaFace
import cv2
from celery import shared_task
from werkzeug.utils import secure_filename
import os

# Specify which GPU to use
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Replace with your desired GPU index

# Allow dynamic allocation of GPU memory
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

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


def save_captured_frames(captured_frames, captures_folder):
    captured_frames_list = []
    
    for captured_frame in captured_frames:
        filename = secure_filename(captured_frame.filename)
        captured_path = os.path.join(captures_folder, filename)
        captured_frame.save(captured_path)

        captured_frames_list.append({"path": captured_path, "filename": filename})
    
    return captured_frames_list


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