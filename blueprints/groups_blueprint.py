from flask import Flask, flash, render_template, Response, request, send_file, redirect, url_for, jsonify, Blueprint
from flask_login import current_user
from models import db, Users, Groups
import os
import json
from datetime import time
from werkzeug.security import check_password_hash

groups_blueprint = Blueprint('groups', __name__)

@groups_blueprint.route('/group-locations/<int:group_id>', methods=['GET'])
def group_locations(group_id):
    group = Groups.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group does not exist'}), 404
    
    owner_dict = {
        "id": group.owner.id, 
        "email": group.owner.email,
        "image": group.owner.identity_image,
        'name': group.owner.user_info.full_name,
    }
    
    group_dict = {
        "id": group.id, 
        "name": group.group_name,
        "code": group.group_code,
        "start_time": group.start_time.strftime('%H:%M:%S') if group.start_time else None,
        "end_time": group.end_time.strftime('%H:%M:%S') if group.end_time else None,
        "members_count": len(group.members),
        "locations_count": len(group.locations),
    }
    
    return jsonify({
        'owner': owner_dict,
        'group': group_dict,
        'members': [
            {
                'id': member.id, 
                'email': member.email, 
                'name': member.user_info.full_name,
                'image': member.identity_image,
            }
            for member in group.members
        ],
        'locations': [
            {'id': location.id, 'name': location.location_name}
            for location in group.locations
        ]
    })

@groups_blueprint.route('/joined-groups/<int:user_id>', methods=['GET'])
def joined_groups(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'joined_groups': [
            {
                'id': group.id, 
                'name': group.group_name, 
                'locations': [
                    {'id': location.id, 'name': location.location_name}
                    for location in group.locations
                ],
            }
            for group in user.joined_groups
        ],
    })



@groups_blueprint.route('/created-groups/<int:user_id>', methods=['GET'])
def created_groups(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'created_groups': [
            {
                'id': group.id, 
                'name': group.group_name, 
                'code': group.group_code, 
                'locations': [
                    {'id': location.id, 'name': location.location_name}
                    for location in group.locations
                ],
            }
            for group in user.created_groups
        ],
    })


from datetime import time
from sqlalchemy.exc import SQLAlchemyError

@groups_blueprint.route('/create', methods=['POST'])
def create():
    data = request.json
    group_name = data.get('group_name')
    user_id = data.get('user_id')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    if not group_name:
        return jsonify({'error': 'Group name is required'}), 400

    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User does not exist'}), 400

    try:
        start_time = (
            time.fromisoformat(start_time_str) if start_time_str else None
        )  
        end_time = (
            time.fromisoformat(end_time_str) if end_time_str else None
        ) 
    except ValueError:
        return jsonify({'error': 'Invalid time format. Use HH:MM:SS'}), 400

    new_group = Groups(
        group_name=group_name,
        user_id=user_id,
        start_time=start_time,
        end_time=end_time,
    )

    try:
        db.session.add(new_group)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    # Prepare response
    group_dict = {
        "id": new_group.id,
        "name": new_group.group_name,
        "code": new_group.group_code,
        "start_time": new_group.start_time.strftime('%H:%M:%S') if new_group.start_time else None,
        "end_time": new_group.end_time.strftime('%H:%M:%S') if new_group.end_time else None,
    }

    return jsonify({'group': group_dict}), 201



@groups_blueprint.route('/join', methods=['POST'])
def join():
    data = request.json
    group_code = data.get('group_code')
    user_id = data.get('user_id')

    if not group_code and not user_id:
        return jsonify({'error': 'Group code and user id are required'}), 400

    group = Groups.query.filter_by(group_code=group_code).first()
    if not group:
        return jsonify({'error': 'Invalid group code'}), 404

    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User does not exist'}), 400

    if user in group.members:
        return jsonify({'error': 'You are already a member of this group'}), 400

    if user.id == group.owner.id:
        return jsonify({'error': 'You cannot join your own group'}), 400

    user.joined_groups.append(group)
    db.session.commit()
    
    group_dict = {
        "id": group.id, 
        "name": group.group_name,
        "code": group.group_code
    }

    return jsonify({'group': group_dict}), 200


@groups_blueprint.route('/update', methods=['POST'])
def update():
    data = request.json
    new_group_name = data.get('new_group_name')
    group_id = data.get('group_id')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')


    if not new_group_name:
        return jsonify({'error': 'Group name is required'}), 400

    group = Groups.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group does not exist'}), 400
    
    try:
        start_time = (
            time.fromisoformat(start_time_str) if start_time_str else None
        )  
        end_time = (
            time.fromisoformat(end_time_str) if end_time_str else None
        ) 
    except ValueError:
        return jsonify({'error': 'Invalid time format. Use HH:MM:SS'}), 400

    group.group_name = new_group_name
    group.start_time = start_time
    group.end_time = end_time
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  
        return jsonify({'error': 'Failed to update group'}), 500    
    
    group_dict = {
        "id": group.id, 
        "name": group.group_name,
        "code": group.group_code,
        "start_time": group.start_time.strftime('%H:%M:%S') if group.start_time else None,
        "end_time": group.end_time.strftime('%H:%M:%S') if group.end_time else None,

    }
    
    return jsonify({'group': group_dict}), 200


@groups_blueprint.route('/delete', methods=['POST'])
def delete():
    data = request.json
    group_id = data.get('group_id')
    user_id = data.get('user_id')
    group_name = data.get('group_name')
    
    group = Groups.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group does not exist'}), 404
    
    if not user_id == group.owner.id:
        return jsonify({"error": "You are not authorized to delete this group!"}), 400
    
    if not group_name:
        return jsonify({"error": "Group name is required to delete the group!"}), 400
    
    if not group_name == group.group_name:
        return jsonify({"error": "You've entered the group name incorrectly."}), 400

    
    db.session.delete(group)
    db.session.commit()
    
    return jsonify({"message": "Group deleted successfully"}), 200
