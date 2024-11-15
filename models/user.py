from . import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


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


class UserInfos(db.Model):
    id = db.Column(Integer, primary_key=True)
    firstname = db.Column(String(255), nullable=False)
    middlename = db.Column(String(255), nullable=False)
    lastname = db.Column(String(255), nullable=False)
    user_id = db.Column(BigInteger, ForeignKey('users.id', ondelete="CASCADE"))

    user = relationship('Users', back_populates='user_info')
    
    def __repr__(self):
        return f'<UserInfo {self.lastname}>'