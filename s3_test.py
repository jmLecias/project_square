import boto3
from botocore.exceptions import NoCredentialsError

s3 = boto3.client()

BUCKET_NAME = 'projectsquare-bucket'
FOLDER_NAME = 'face-database/'

IMAGE_FILE = './faces/database/class3/John-Mark-Lecias.jpg'
IMAGE_KEY = FOLDER_NAME + 'john-marks.jpg'

try:
    s3.upload_file(IMAGE_FILE, BUCKET_NAME, IMAGE_KEY)
    print(f'Image uploaded successfully.')
except NoCredentialsError:
    print(f'Credentials not found. Please check AWS credentials.')
except Exception as e:
    print(f'Error uploading image {e}')


response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=FOLDER_NAME)
for obj in response['Contents']:
    print(obj['Key'])