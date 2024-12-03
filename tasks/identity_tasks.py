from celery import shared_task, group
import boto3
from botocore.exceptions import NoCredentialsError
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME, FOLDER_NAME
from celery.exceptions import Ignore
from models import db, UserInfos, FaceImages, Users
from redis.commands.search.field import VectorField, TagField
from redis.commands.search.query import Query
import numpy as np
from deepface import DeepFace
import os
import uuid
import time
from utils.redis_utils import redis_db
from utils.db_utils import initialize_db

initialize_db()

# Enable GPU
# os.environ["CUDA_VISIBLE_DEVICES"] = "0" 
# os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

s3 = boto3.client(
    's3', 
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name = AWS_REGION
)


@shared_task
def save_face_embeddings(face_image_path, unique_key):
    # When saving fails, there must be a way to check redis db if unique_key exists

    try:
         embedding = DeepFace.represent(
            img_path=face_image_path,
            model_name="ArcFace",
            detector_backend="retinaface",
        )[0]["embedding"]
    finally:
        os.remove(face_image_path)

    try:
        pipeline = redis_db.pipeline(transaction=False)

        key = unique_key
        value = np.array(embedding).astype(np.float32).tobytes()
        pipeline.hset(key, mapping={"embedding": value})

        pipeline.execute()
    except Exception as e:
        return (f'Error saving face embeddings {e}')
        
    return (f'Successfully saved face embeddings to redis DB')

# For each face_image of user
# perform similarity checks on each picture to 
# ensure they are of the same person (use the default profile face[0])


@shared_task(bind=True)
def identity_upload(self, face_image_paths, personal_info, user_id):
    
    # add new user info here using personal info
    new_user_info = UserInfos(
        firstname = personal_info['firstname'],
        middlename = personal_info['middlename'],
        lastname = personal_info['lastname'],
        user_id = user_id
    )

    db.session.add(new_user_info)
    db.session.commit()

    uploaded_images = []
    for face_image_path in face_image_paths:
        try:
            unique_key = str(uuid.uuid4()) 
            filename = unique_key + ".png"
            bucket_path = FOLDER_NAME + f'{user_id}/' + filename

            new_face_image = FaceImages(
                unique_key = unique_key,
                bucket_path = bucket_path,
                user_id = user_id
            )
                
            s3.upload_file(face_image_path, BUCKET_NAME, bucket_path)

            db.session.add(new_face_image)
            db.session.commit()

            uploaded_image_dict ={
                "unique_key": unique_key,
                "face_image_path": face_image_path
            }

            uploaded_images.append(uploaded_image_dict)
        except NoCredentialsError:
            print(f'Credentials not found. Please check AWS credentials.')
            db.session.rollback()
        except Exception as e:
            print(f'Error uploading image {e}')
            db.session.rollback()

    return uploaded_images


@shared_task(bind=True)
def update_faces(self, face_image_paths, user_id):
    user = Users.query.filter_by(id=user_id).first()

    for face_image in user.face_images:
        try:
            redis_db.delete(face_image.unique_key)
        except Exception as e:
            print(f"Error deleting Redis key {face_image.unique_key}: {e}")
        db.session.delete(face_image)

    db.session.commit()

    print("Previous face images cleared")

    uploaded_images = []
    for face_image_path in face_image_paths:
        try:
            unique_key = str(uuid.uuid4()) 
            filename = unique_key + ".png"
            bucket_path = FOLDER_NAME + f'{user_id}/' + filename

            new_face_image = FaceImages(
                unique_key = unique_key,
                bucket_path = bucket_path,
                user_id = user_id
            )
                
            s3.upload_file(face_image_path, BUCKET_NAME, bucket_path)

            db.session.add(new_face_image)
            db.session.commit()

            uploaded_image_dict ={
                "unique_key": unique_key,
                "face_image_path": face_image_path
            }

            uploaded_images.append(uploaded_image_dict)
        except NoCredentialsError:
            print(f'Credentials not found. Please check AWS credentials.')
            db.session.rollback()
        except Exception as e:
            print(f'Error uploading image {e}')
            db.session.rollback()

    return uploaded_images