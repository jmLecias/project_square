from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    id = db.Column(BigInteger, primary_key=True)
    email = db.Column(String(255), nullable=False, unique=True)
    password= db.Column(String(255), nullable=True)
    user_type_id = db.Column(Integer, ForeignKey('user_types.id'), default=1)
    
    user_type = relationship('UserTypes', backref='users')
    
    created_groups = relationship('Groups', back_populates=('owner'))
    joined_groups = relationship('Groups', secondary='group_user')

    def __repr__(self):
        return f'<User {self.firstname} {self.lastname}>'
    def get_id(self):
        return f'{self.id}'
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)

class UserTypes(db.Model):
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(50), nullable=False)

    def __repr__(self):
        return f'<UserType {self.name}>'

group_user = Table('group_user', db.Model.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('user_id', BigInteger, ForeignKey('users.id'))
)

class Groups(db.Model):
    id = db.Column(Integer, primary_key=True)
    group_name = db.Column(String(100), nullable=False)
    user_id = db.Column(BigInteger, ForeignKey('users.id'))
    group_code = db.Column(String(6), unique=True, nullable=False)
    
    owner = relationship('Users', back_populates='created_groups')
    members = relationship('Users', secondary='group_user')
    locations = relationship('Locations', backref='group')

    def __repr__(self):
        return f'<Group {self.group_name}>'
    def __init__(self, group_name, user_id):
        self.group_name = group_name
        self.user_id = user_id
        self.generate_group_code()
    def generate_group_code(self):
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not Groups.query.filter_by(group_code=code).first():
                self.group_code = code
                break

class Locations(db.Model):
    id = db.Column(Integer, primary_key=True)
    location_name = db.Column(String(200), nullable=False)
    
    group_id = db.Column(Integer, ForeignKey('groups.id'))
    cameras = relationship('Cameras', backref='location')

    def __repr__(self):
        return f'<Location {self.location_name}>'

class Cameras(db.Model):
    id = db.Column(Integer, primary_key=True)
    ip_address = db.Column(String(20), nullable=False)
    camera_name = db.Column(String(100), nullable=False)
    
    location_id = db.Column(Integer, ForeignKey('locations.id'))

    def __repr__(self):
        return f'<Camera {self.camera_name}>'
