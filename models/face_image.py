from . import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship
import boto3
from botocore.exceptions import NoCredentialsError
from config import *

s3 = boto3.client(
    's3', 
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name = AWS_REGION
)

class FaceImages(db.Model):
    id = db.Column(Integer, primary_key=True)
    unique_key = db.Column(String(255), nullable=False, unique=True)
    bucket_path = db.Column(String(255), nullable=False)
    user_id = db.Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"))

    user = relationship('Users', back_populates='face_images')

    @property
    def presigned_url(self):
        """
        Returns a pre-signed URL of the face image's bucket_path from S3.
        """
        try:
            params = {
                'Bucket': BUCKET_NAME,
                'Key': self.bucket_path,
            }
            presigned_url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=7200)
            return presigned_url
        except NoCredentialsError:
            return None  # Return None if AWS credentials are missing
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def __repr__(self):
        return f'<FaceImage {self.unique_key}>'