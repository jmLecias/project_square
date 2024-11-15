from . import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Locations(db.Model):
    id = db.Column(Integer, primary_key=True)
    location_name = db.Column(String(200), nullable=False)
    group_id = db.Column(Integer, ForeignKey('groups.id', ondelete='CASCADE')) 
    
    cameras = relationship('Cameras', backref='location', cascade='all, delete-orphan') 
    detections = relationship('DetectionRecords', back_populates='location')
    
    def __repr__(self):
        return f'<Location {self.location_name}>'
