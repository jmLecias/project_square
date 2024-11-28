from flask import Flask, flash, render_template, Response, request, send_file, redirect, url_for, jsonify, Blueprint
from flask_login import current_user
from models import db, Locations, Groups
import os
from werkzeug.security import check_password_hash

locations_blueprint = Blueprint('locations', __name__)

@locations_blueprint.route('/location-cameras/<int:location_id>', methods=['GET'])
def group_locations(location_id):
    location = Locations.query.filter_by(id=location_id).first()
    if not location:
        return jsonify({'error': 'Location does not exist'}), 404
    
    location_dict = {
        "id": location.id, 
        "name": location.location_name
    }
    
    group_dict = {
        "id": location.group.id, 
        "name": location.group.group_name
    }

    cameras = [
        {
            'id': camera.id, 
            'name': camera.camera_name, 
            'rtsp_url': camera.rtsp_url,
            'location_id': location.id,
            'group_id': location.group.id,
        }
        for camera in location.cameras
    ]

    detections = [
        {
            'id': detection.id, 
            'status': detection.status.status
        }
        for detection in location.detections_today
    ]
    
    return jsonify({
        'group': group_dict,
        'location': location_dict,
        'cameras': cameras,
        'detections': detections,
    })


@locations_blueprint.route('/location-records-info/<int:location_id>', methods=['GET'])
def location_records_info(location_id):
    location = Locations.query.filter_by(id=location_id).first()
    if not location:
        return jsonify({'error': 'Location does not exist'}), 404
    
    location_dict = {
        "id": location.id, 
        "owner_id": location.group.owner.id,
        "name": location.location_name
    }

    users = [
        {
            'id': location.group.owner.id,
            'name': location.group.owner.user_info.full_name
        }
    ] + [
        {
            'id': member.id,
            'name': member.user_info.full_name
        }
         for member in location.group.members if member.has_identity
    ]
    
    return jsonify({
        'location': location_dict,
        'users': users,
    }), 200


@locations_blueprint.route('/create', methods=['POST'])
def create():
    data = request.json
    location_name = data.get('location_name')
    group_id = data.get('group_id')

    if not location_name:
        return jsonify({'error': 'Location name is required'}), 400

    group = Groups.query.filter_by(id=group_id).first()
    if not group:
        return jsonify({'error': 'Group does not exist'}), 400

    new_location = Locations(
        location_name=location_name,
        group_id=group_id
    )
    
    db.session.add(new_location)
    db.session.commit()
    
    location_dict = {
        "id": new_location.id, 
        "name": new_location.location_name,
    }

    return jsonify({'location': location_dict}), 201



@locations_blueprint.route('/delete', methods=['POST'])
def delete():
    data = request.json
    location_id = data.get('location_id')
    owner_password = data.get('owner_password')
    
    location = Locations.query.filter_by(id=location_id).first()
    if not location:
        return jsonify({'error': 'Location does not exist'}), 404
    
    if not owner_password:
        return jsonify({"error": "Owner's password is required when deleting a location"}), 400
    
    if not check_password_hash(location.group.owner.password, owner_password):
        return jsonify({"error": "You are not authorized to delete this location"}), 401
    
    db.session.delete(location)
    db.session.commit()
    
    return jsonify({"message": "Location deleted successfully"}), 200
