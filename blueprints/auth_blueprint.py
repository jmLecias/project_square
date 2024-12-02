from flask import request, jsonify, Blueprint
from flask_login import LoginManager, login_user, logout_user
from sqlalchemy import func
from models import db, Users, DetectionRecords
from utils.dashboard_utils import get_user_detections_days_count, get_location_detections_day_count, get_location_detections_days_count

auth_blueprint = Blueprint('auth', __name__)

# Default auth 
@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = Users.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Add security token: JWT
    login_user(user)
    
    user_dict = {
        "id": user.id, 
        "email": user.email,
        "name": user.user_info.full_name if user.user_info else None,
        "image": user.identity_image if user.has_identity else None,
        "session_timeout": 7200,
    }
    
    return jsonify({'user': user_dict}), 200


@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    new_user = Users(
        email=email
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)

    user_dict = {"id": new_user.id, "email": new_user.email}

    return jsonify({'user': user_dict}), 201


@auth_blueprint.route('/logout', methods=['POST'])
# @login_required // needs authorization token something...
def logout():
    logout_user()
    return jsonify({'message': 'Log out successful'}), 200


@auth_blueprint.route('/dashboard-data/<int:user_id>', methods=['GET'])
def dashboard_data_route(user_id):

    if not user_id:
        return jsonify({'error': 'User id is required'}), 400

    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User does not exist'}), 400
    
    detections = (
        DetectionRecords.query
        .filter_by(user_id=user_id)
        .order_by(DetectionRecords.datetime.desc())  
        .limit(10)
        .all()
    )

    recent_detections = [
        {
            'id': detection.id, 
            'datetime': detection.datetime,
            'detection': detection.detected_path,
            'origin': detection.origin_path,
            'location': detection.location.location_name,
            'group': detection.location.group.group_name
        }
        for detection in detections
    ]

    location_day_count = [
        get_location_detections_day_count(location, 7)
        for group in user.created_groups
        for location in group.locations
    ]
    
    location_days_count = [
        get_location_detections_days_count(location, 7)
        for group in user.created_groups
        for location in group.locations
    ]

    doughnut_data = {
        "locations": [
            item["location"] for item in location_days_count
        ],
        "data": [
            item["count"] for item in location_days_count
        ]
    }
    
    dashboard_data_dict = {
        "detections_count": len(user.detections_today), 
        "created_count": len(user.created_groups),
        "joined_count": len(user.joined_groups),
        "recent_detections": recent_detections,
        "bar_data": get_user_detections_days_count(user_id, 7),
        "line_data": location_day_count,
        "doughnut_data": doughnut_data,
    }
    
    return jsonify({'dashboard_data': dashboard_data_dict}), 200