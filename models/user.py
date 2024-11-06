from . import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model, UserMixin):
    id = db.Column(BigInteger, primary_key=True)
    email = db.Column(String(255), nullable=False, unique=True)
    password = db.Column(String(255), nullable=True)
    
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
