from . import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date

class Locations(db.Model):
    id = db.Column(Integer, primary_key=True)
    location_name = db.Column(String(200), nullable=False)
    group_id = db.Column(Integer, ForeignKey('groups.id', ondelete='CASCADE')) 
    
    cameras = relationship('Cameras', backref='location', cascade='all, delete-orphan') 
    detections = relationship('DetectionRecords', back_populates='location')
    
    @property
    def detections_today(self):
        """Returns detections recorded today."""
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        return [d for d in self.detections if start_of_day <= d.datetime < end_of_day]
    
    def __repr__(self):
        return f'<Location {self.location_name}>'
