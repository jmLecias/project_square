from flask import request, jsonify, Blueprint
from models import db, Cameras
from werkzeug.security import check_password_hash

cameras_blueprint = Blueprint('cameras', __name__)


@cameras_blueprint.route('/create', methods=['POST'])
def create():
    data = request.json
    camera_name = data.get('camera_name')
    rtsp_url = data.get('rtsp_url')
    location_id = data.get('location_id')

    if not camera_name or not rtsp_url or not location_id:
        return jsonify({'error': 'Camera name and rtsp url and location id is required'}), 400

    new_camera = Cameras(
        camera_name=camera_name,
        rtsp_url=rtsp_url,
        location_id=location_id,
        type_id=1,
    )
    
    db.session.add(new_camera)
    db.session.commit()

    return jsonify({'message': "Camera added successfully!"}), 201



@cameras_blueprint.route('/update', methods=['POST'])
def update():
    data = request.json
    camera_id = data.get('camera_id')
    camera_name = data.get('camera_name')
    rtsp_url = data.get('rtsp_url')

    if not camera_name or not rtsp_url:
        return jsonify({'error': 'Camera name and rtsp url is required'}), 400

    camera = Cameras.query.filter_by(id=camera_id).first()
    if not camera:
        return jsonify({'error': 'Camera does not exist'}), 400
    
    camera.camera_name = camera_name
    camera.rtsp_url = rtsp_url
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  
        return jsonify({'error': 'Failed to update camera'}), 500    
    
    
    return jsonify({'message': "Camera updated successfully!"}), 200



@cameras_blueprint.route('/delete', methods=['POST'])
def delete():
    data = request.json
    camera_id = data.get('camera_id')

    if not camera_id:
        return jsonify({'error': 'Camera id is required'}), 400

    camera = Cameras.query.filter_by(id=camera_id).first()
    if not camera:
        return jsonify({'error': 'Camera does not exist'}), 400
    
    db.session.delete(camera)
    db.session.commit()

    return jsonify({"message": "Camera deleted successfully"}), 200
