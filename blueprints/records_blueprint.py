from flask import jsonify, Blueprint, request
from models import db, Users, DetectionRecords, Locations

records_blueprint = Blueprint('records', __name__)

@records_blueprint.route('/user-records', methods=['POST'])
def user_records():
    data = request.get_json()
    user_id = data.get('user_id')
    page = data.get('page', 1)
    per_page = data.get('per_page', 10)

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    if not isinstance(page, int) or not isinstance(per_page, int):
        return jsonify({'error': 'page and per_page must be integers'}), 400

    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    detections_query = DetectionRecords.query.filter_by(user_id=user_id)
    if not detections_query:
        return jsonify({'error': 'No detections found for this user'}), 404

    total_records = detections_query.count()
    total_pages = (total_records + per_page - 1) // per_page  # Calculate total pages

    paginated_detections = detections_query.offset((page - 1) * per_page).limit(per_page).all()

    detections = [
        {
            'detection': detection.detected_path, 
            'datetime': detection.datetime, 
            'location': detection.location.location_name, 
            'user': user.user_info.full_name,
            'confidence': detection.confidence, 
            'status': detection.status.status
        }
        for detection in paginated_detections
    ]

    # Return paginated response
    return jsonify({
        'detections': detections,
        'pagination': {
            'total_records': total_records,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }
    }), 200

@records_blueprint.route('/location-records', methods=['POST'])
def location_records():
    data = request.get_json()
    location_id = data.get('location_id')
    page = data.get('page', 1)
    per_page = data.get('per_page', 10)

    if not location_id:
        return jsonify({'error': 'location id is required'}), 400
    if not isinstance(page, int) or not isinstance(per_page, int):
        return jsonify({'error': 'page and per_page must be integers'}), 400

    location = Locations.query.filter_by(id=location_id).first()
    if not location:
        return jsonify({'error': 'Location not found'}), 404

    detections_query = DetectionRecords.query.filter_by(location_id=location_id)
    if not detections_query:
        return jsonify({'error': 'No detections found for this user'}), 404

    total_records = detections_query.count()
    total_pages = (total_records + per_page - 1) // per_page  # Calculate total pages

    paginated_detections = detections_query.offset((page - 1) * per_page).limit(per_page).all()

    detections = [
        {
            'detection': detection.detected_path, 
            'datetime': detection.datetime, 
            'location': detection.location.location_name, 
            'user': detection.user.user_info.full_name if detection.user else "Unknown",
            'confidence': detection.confidence, 
            'status': detection.status.status
        }
        for detection in paginated_detections
    ]

    # Return paginated response
    return jsonify({
        'detections': detections,
        'pagination': {
            'total_records': total_records,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }
    }), 200

@records_blueprint.route('/location-user-records', methods=['POST'])
def location_user_records():
    data = request.get_json()
    location_id = data.get('location_id')
    user_id = data.get('user_id')
    page = data.get('page', 1)
    per_page = data.get('per_page', 10)

    if not location_id:
        return jsonify({'error': 'location id is required'}), 400
    if not isinstance(page, int) or not isinstance(per_page, int):
        return jsonify({'error': 'page and per_page must be integers'}), 400

    location = Locations.query.filter_by(id=location_id).first()
    if not location:
        return jsonify({'error': 'Location not found'}), 404

    detections_query = DetectionRecords.query.filter_by(location_id=location_id, user_id=user_id)
    if not detections_query:
        return jsonify({'error': 'No detections found for this user'}), 404

    total_records = detections_query.count()
    total_pages = (total_records + per_page - 1) // per_page  # Calculate total pages

    paginated_detections = detections_query.offset((page - 1) * per_page).limit(per_page).all()

    detections = [
        {
            'detection': detection.detected_path, 
            'datetime': detection.datetime, 
            'location': detection.location.location_name, 
            'user': detection.user.user_info.full_name if detection.user else "Unknown",
            'confidence': detection.confidence, 
            'status': detection.status.status
        }
        for detection in paginated_detections
    ]

    # Return paginated response
    return jsonify({
        'detections': detections,
        'pagination': {
            'total_records': total_records,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }
    }), 200
