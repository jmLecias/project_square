from flask import Flask
from celery import shared_task, group
import boto3
from botocore.exceptions import NoCredentialsError
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME, FOLDER_NAME
from celery.exceptions import Ignore
from models import db, UserInfos, FaceImages
from redis.commands.search.field import VectorField, TagField
from redis.commands.search.query import Query
import redis
import numpy as np
from deepface import DeepFace
import os
import uuid
import time

# Initialize Flask app context (without running the app)
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@192.168.254.102:3306/project_square'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Enable GPU
# os.environ["CUDA_VISIBLE_DEVICES"] = "0" 
# os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

s3 = boto3.client(
    's3', 
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name = AWS_REGION
)

# temporary, will use redis on local redis server instead of online 
r = redis.Redis(
    host = "redis-13209.c292.ap-southeast-1-1.ec2.redns.redis-cloud.com",
    port = 13209,
    password = "irKVnFOjVdss02m0NV4mBv5bCHfbOoT3",
    ssl = False,
)


@shared_task
def save_face_embeddings(face_image_path, unique_key):
    # When saving fails, there must be a way to check redis db if unique_key exists

    # Extract face embeddings using ArcFace
    try:
         embedding = DeepFace.represent(
            img_path=face_image_path,
            model_name="ArcFace",
            detector_backend="retinaface",
        )[0]["embedding"]
    finally:
        os.remove(face_image_path)

     # Put embeddings in Redis Database
    try:
        pipeline = r.pipeline(transaction=False)

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