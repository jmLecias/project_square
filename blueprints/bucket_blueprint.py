from flask import  jsonify, Blueprint
from models import *
import os
import boto3
from botocore.exceptions import NoCredentialsError

bucket_blueprint = Blueprint('bucket', __name__)

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = "ap-southeast-1"
BUCKET_NAME = 'projectsquare-bucket'
FOLDER_NAME = 'face-database/'

s3 = boto3.client(
    's3', 
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name = AWS_REGION
)

@bucket_blueprint.route('/get/<string:image_name>', methods=['GET'])
def get_image_presigned_url(image_name):
    try:
        params = {
            'Bucket': BUCKET_NAME,
            'Key': FOLDER_NAME + image_name,
        }
        presigned_url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=5)
        return jsonify({'url': presigned_url})
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not found'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

