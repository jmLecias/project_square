import os 

CAPTURES_FOLDER = 'faces/captures'
DETECTIONS_FOLDER = 'faces/detections'
FACE_DATABASE = 'faces/database/class3'
TEMP_FOLDER = 'faces/temp'


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = "ap-southeast-1"
BUCKET_NAME = 'projectsquare-bucket'
FOLDER_NAME = 'face-database/'