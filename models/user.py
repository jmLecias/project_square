from . import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, desc
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
from botocore.exceptions import NoCredentialsError
from config import *

s3 = boto3.client(
    's3', 
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name = AWS_REGION
)

class Users(db.Model, UserMixin):
    id = db.Column(BigInteger, primary_key=True)
    email = db.Column(String(255), nullable=False, unique=True)
    password = db.Column(String(255), nullable=True)
    
    user_info = relationship('UserInfos', uselist=False, back_populates='user', cascade="all, delete-orphan")
    face_images = relationship('FaceImages', back_populates='user', cascade="all, delete-orphan")
    
    detections = relationship('DetectionRecords', back_populates='user')
    daily_records = relationship('DailyRecords', back_populates='user')
    
    created_groups = relationship('Groups', back_populates='owner')
    joined_groups = relationship('Groups', secondary='group_user')

    def __repr__(self):
        return f'<User {self.email}>'

    def get_id(self):
        return f'{self.id}'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def has_identity(self):
        """
        Checks if the user has a linked `user_info` and at least one `face_image`.
        """
        return self.user_info is not None and len(self.face_images) > 0
    
    @property
    def identity_image(self):
        """
        Returns a pre-signed URL for the user's image from S3.
        """
        if not self.face_images:
            return None  # No face image available
        
        # Assuming the first image in the relationship is the one to use
        face_image = self.face_images[0]
        try:
            params = {
                'Bucket': BUCKET_NAME,
                'Key': face_image.bucket_path,
            }
            presigned_url = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=7200)
            return presigned_url
        except NoCredentialsError:
            return None  # Return None if AWS credentials are missing
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def latest_detection_matches_type(self, type_id):
        """
        Checks if the latest detection record's type_id matches the given type_id.
        """
        if not self.detections:
            return False  # No detections available

        latest_detection = max(self.detections, key=lambda d: d.datetime)

        return latest_detection.type_id == type_id


class UserInfos(db.Model):
    id = db.Column(Integer, primary_key=True)
    firstname = db.Column(String(255), nullable=False)
    middlename = db.Column(String(255), nullable=False)
    lastname = db.Column(String(255), nullable=False)
    user_id = db.Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"))

    user = relationship('Users', back_populates='user_info')
    
    @property
    def full_name(self):
        middle_initial = self.middlename[0] + '.' if self.middlename else ''
        return f'{self.firstname} {middle_initial} {self.lastname}'
    
    def __repr__(self):
        return f'<UserInfo {self.lastname}>'