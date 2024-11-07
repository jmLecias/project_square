from . import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

class FaceImages(db.Model):
    id = db.Column(Integer, primary_key=True)
    unique_key = db.Column(String(255), nullable=False, unique=True)
    filename = db.Column(String(255), nullable=False)
    user_id = db.Column(BigInteger, ForeignKey('users.id'))

    user = relationship('Users', back_populates='face_images')

    def __repr__(self):
        return f'<FaceImage {self.unique_key}>'