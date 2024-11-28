from . import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import SMALLINT

class Cameras(db.Model):
    id = db.Column(Integer, primary_key=True)
    rtsp_url = db.Column(String(255), nullable=False)
    camera_name = db.Column(String(100), nullable=False)
    
    type_id = db.Column(Integer, ForeignKey('camera_types.id'), nullable=False)
    location_id = db.Column(Integer, ForeignKey('locations.id', ondelete='CASCADE'))

    type = relationship('CameraTypes', back_populates='cameras')

    def __repr__(self):
        return f'<Camera {self.camera_name}>'

class CameraBrands(db.Model):
    id = db.Column(Integer, primary_key=True)
    brand_name = db.Column(String(100), nullable=False)
    port = db.Column(SMALLINT(unsigned=True), nullable=False)
    stream_path = db.Column(String(50), nullable=False)

    # cameras = relationship('Cameras', back_populates='brand')

    def __repr__(self):
        return f'<CameraBrand {self.brand_name}>'

class CameraTypes(db.Model):
    id = db.Column(Integer, primary_key=True)
    type_name = db.Column(String(100), nullable=False)

    cameras = relationship('Cameras', back_populates='type')
    detections = relationship('DetectionRecords', back_populates='type')
    
    def __repr__(self):
        return f'<CameraType {self.type_name}>'


def seed_cameras():
    if not CameraTypes.query.filter_by(type_name="Entrance").first():
        entrance_type = CameraTypes(id=1, type_name="Entrance")
        db.session.add(entrance_type)
    
    if not CameraTypes.query.filter_by(type_name="Exit").first():
        exit_type = CameraTypes(id=2, type_name="Exit")
        db.session.add(exit_type)

    if not CameraBrands.query.filter_by(brand_name="V380").first():
        v380_brand = CameraBrands(id=1, brand_name="V380", stream_path="/live/ch00_0", port="554")
        db.session.add(v380_brand)
    
    if not CameraBrands.query.filter_by(brand_name="Tapo").first():
        tapo_brand = CameraBrands(id=2, brand_name="Tapo", stream_path="/stream1", port="554")
        db.session.add(tapo_brand)

    db.session.commit()
    print("Camera brands and types seeded successfully.")
