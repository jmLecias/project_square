from . import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Time, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import SMALLINT, BIGINT

class DetectionRecords(db.Model):
    __tablename__ = 'detection_records'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    type_id = Column(Integer, ForeignKey('camera_types.id'), nullable=False)
    image_origin_path = Column(String(255), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    type = relationship('CameraTypes', back_populates='detections')
    user = relationship('Users', back_populates='detections')
    location = relationship('Locations', back_populates='detections')

    def __repr__(self):
        return f'<DetectionRecord {self.id} - {self.datetime}>'
    

class DailyRecords(db.Model):
    __tablename__ = 'daily_records'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    arrival = Column(Time, nullable=True)
    departure = Column(Time, nullable=True)
    undertime = Column(BIGINT, nullable=True)  # Storing undertime in seconds
    overtime = Column(BIGINT, nullable=True)   # Storing overtime in seconds
    am_time_in = Column(Time, nullable=True)
    am_time_out = Column(Time, nullable=True)
    pm_time_in = Column(Time, nullable=True)
    pm_time_out = Column(Time, nullable=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    user = relationship('Users', back_populates='daily_records')

    def __repr__(self):
        return f'<DailyRecord {self.id} - {self.date}>'