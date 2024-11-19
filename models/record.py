from . import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Time, BigInteger, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import SMALLINT, BIGINT

class DetectionRecords(db.Model):
    __tablename__ = 'detection_records'

    id = Column(BigInteger, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    confidence = Column(Float,  nullable=False)
    origin_path = Column(String(255), nullable=False)
    detected_path = Column(String(255), nullable=False)
    type_id = Column(Integer, ForeignKey('camera_types.id'), nullable=True)
    location_id = Column(Integer, ForeignKey('locations.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    status_id = Column(Integer, ForeignKey('detection_status.id'), nullable=False)
    identity_key = Column(String(255), nullable=True)

    status = relationship('DetectionStatus', back_populates='detections')
    type = relationship('CameraTypes', back_populates='detections')
    user = relationship('Users', back_populates='detections')
    location = relationship('Locations', back_populates='detections')

    def __repr__(self):
        return f'<DetectionRecord {self.id} - {self.datetime}>'


class DetectionStatus(db.Model):
    id = db.Column(Integer, primary_key=True)
    status = db.Column(String(100), nullable=False)

    detections = relationship('DetectionRecords', back_populates='status')
    
    def __repr__(self):
        return f'<DetectionStatus {self.status}>'
    

class DailyRecords(db.Model):
    __tablename__ = 'daily_records'

    id = Column(BigInteger, primary_key=True)
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

   
def seed_status():
    if not DetectionStatus.query.filter_by(status="Detected").first():
        detection_status = DetectionStatus(id=1, status="Detected")
        db.session.add(detection_status)

    if not DetectionStatus.query.filter_by(status="Recognized").first():
        detection_status = DetectionStatus(id=2, status="Recognized")
        db.session.add(detection_status)

    if not DetectionStatus.query.filter_by(status="Unknown").first():
        detection_status = DetectionStatus(id=3, status="Unknown")
        db.session.add(detection_status)

    db.session.commit()
    print("Detection status seeded successfully.")
