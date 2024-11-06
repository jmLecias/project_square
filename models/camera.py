from . import db
from sqlalchemy import Column, Integer, String, ForeignKey

class Cameras(db.Model):
    id = db.Column(Integer, primary_key=True)
    ip_address = db.Column(String(20), nullable=False)
    camera_name = db.Column(String(100), nullable=False)
    
    location_id = db.Column(Integer, ForeignKey('locations.id'))

    def __repr__(self):
        return f'<Camera {self.camera_name}>'
