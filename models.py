from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Table
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    id = db.Column(BigInteger, primary_key=True)
    firstname = db.Column(String(100), nullable=False)
    middlename = db.Column(String(100))
    lastname = db.Column(String(100), nullable=False)
    email = db.Column(String(255), nullable=False, unique=True)
    password= db.Column(String(255), nullable=False)
    
    user_type_id = db.Column(Integer, ForeignKey('user_types.id'))
    user_type = relationship('UserTypes', backref='users')
    
    groups = relationship('Groups', secondary='group_user', back_populates='users')

    def __repr__(self):
        return f'<User {self.firstname} {self.lastname}>'
    def get_id(self):
        return f'U{self.id}'
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
    
    users = relationship('Users', secondary='group_user', back_populates='groups')
    locations = relationship('Locations', backref='group')

    def __repr__(self):
        return f'<Group {self.group_name}>'

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
