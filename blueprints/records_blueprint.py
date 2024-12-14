from flask import jsonify, Blueprint, request, Response
import pandas as pd
from io import BytesIO
from models import db, Users, DetectionRecords, Locations
from datetime import datetime
import pytz

records_blueprint = Blueprint('records', __name__)

@records_blueprint.route('/download-attendance/<int:location_id>',  methods=['GET'])
def download_attendance(location_id):
    detections = DetectionRecords.query.filter(
        DetectionRecords.location_id == location_id,
        db.func.date(DetectionRecords.datetime) == db.func.current_date()
    ).order_by(DetectionRecords.datetime.asc())  .all()

    if not detections:
        return jsonify({"error": "No detections found for this location today."}), 404
    
    seen_user_ids = set()
    attendance = []

    for detection_record in detections:
        if detection_record.user_id and detection_record.user_id not in seen_user_ids:
            seen_user_ids.add(detection_record.user_id)
            attendance.append(detection_record)
    
    # Sample data
    data = [
        {
            "Datetime": detection_record.datetime,
            "Group Name": detection_record.location.group.group_name,
            "Location Name": detection_record.location.location_name,
            "Firstname": detection_record.user.user_info.firstname if detection_record.user else None,
            "Middlename": detection_record.user.user_info.middlename if detection_record.user else None,
            "Lastname": detection_record.user.user_info.lastname if detection_record.user else None,
            "Status": detection_record.status.status,
            "Percentage": None,
        }
        for detection_record in attendance
    ]
    df = pd.DataFrame(data)
    
    # Save DataFrame to a BytesIO object (in-memory buffer)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    output.seek(0)  # Move the cursor to the beginning of the buffer
    
    # Prepare response with appropriate headers for download
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment;filename=sample_data.xlsx"
        }
    )

@records_blueprint.route('/user-records', methods=['POST'])
def user_records():
    data = request.get_json()
    user_id = data.get('user_id')
    page = data.get('page', 1)
    per_page = data.get('per_page', 10)
    specific_date = data.get('date') 

    specific_date = datetime.fromisoformat(specific_date.replace("Z", "+00:00")) if specific_date else None
    local_timezone = pytz.timezone('Asia/Manila')
    local_datetime = specific_date.astimezone(local_timezone) if specific_date else None

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
    
    if local_datetime:
        detections_query = detections_query.filter(
            db.func.date(DetectionRecords.datetime) == local_datetime.date()
        )
    
    detections_query = detections_query.order_by(DetectionRecords.datetime.desc())
    total_records = detections_query.count()
    total_pages = (total_records + per_page - 1) // per_page  # Calculate total pages

    paginated_detections = detections_query.offset((page - 1) * per_page).limit(per_page).all()

    detections = [
        {
            'origin': detection.origin_path, 
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
    specific_date = data.get('date') 

    specific_date = datetime.fromisoformat(specific_date.replace("Z", "+00:00")) if specific_date else None
    local_timezone = pytz.timezone('Asia/Manila')
    local_datetime = specific_date.astimezone(local_timezone) if specific_date else None

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
    
    if local_datetime:
        detections_query = detections_query.filter(
            db.func.date(DetectionRecords.datetime) == local_datetime.date()
        )

    detections_query = detections_query.order_by(DetectionRecords.datetime.desc())
    total_records = detections_query.count()
    total_pages = (total_records + per_page - 1) // per_page  # Calculate total pages

    paginated_detections = detections_query.offset((page - 1) * per_page).limit(per_page).all()

    detections = [
        {
            'origin': detection.origin_path, 
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
    specific_date = data.get('date') 

    specific_date = datetime.fromisoformat(specific_date.replace("Z", "+00:00")) if specific_date else None
    local_timezone = pytz.timezone('Asia/Manila')
    local_datetime = specific_date.astimezone(local_timezone) if specific_date else None

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

    if local_datetime:
        detections_query = detections_query.filter(
            db.func.date(DetectionRecords.datetime) == local_datetime.date()
        )

    detections_query = detections_query.order_by(DetectionRecords.datetime.desc())
    total_records = detections_query.count()
    total_pages = (total_records + per_page - 1) // per_page  # Calculate total pages

    paginated_detections = detections_query.offset((page - 1) * per_page).limit(per_page).all()

    detections = [
        {
            'origin': detection.origin_path, 
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
