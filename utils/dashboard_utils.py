from flask import jsonify
from sqlalchemy import func
from models import db, Users, DetectionRecords, Locations
from datetime import datetime, timedelta
from utils.db_utils import initialize_db

initialize_db()

def get_user_detections_days_count(user_id, num_of_days):
    now = datetime.now()
    days = [(now - timedelta(days=i)).date() for i in range((num_of_days - 1), -1, -1)]

    detections_by_date = (
        DetectionRecords.query
        .filter(
            DetectionRecords.user_id == user_id,
            DetectionRecords.datetime >= days[0],
        )
        .with_entities(
            func.date(DetectionRecords.datetime).label("day"),
            func.count(DetectionRecords.id).label("count"),
        )
        .group_by("day")
        .all()
    )

    detections_dict = {day: count for day, count in detections_by_date}

    data_dict = {
        "days": [day.strftime("%b %d") for day in days],
        "data": [detections_dict.get(day, 0) for day in days],
    }
    
    return data_dict


def get_location_detections_day_count(location, num_of_days):
    now = datetime.now()
    days = [(now - timedelta(days=i)).date() for i in range((num_of_days - 1), -1, -1)]

    detections_by_date = (
        DetectionRecords.query
        .filter(
            DetectionRecords.location_id == location.id,
            DetectionRecords.datetime >= days[0],
        )
        .with_entities(
            func.date(DetectionRecords.datetime).label("day"),
            func.count(DetectionRecords.id).label("count"),
        )
        .group_by("day")
        .all()
    )

    detections_dict = {day: count for day, count in detections_by_date}

    data_dict = {
        "location": location.location_name,
        "days": [day.strftime("%b %d") for day in days],
        "data": [detections_dict.get(day, 0) for day in days],
    }
    
    return data_dict

def get_location_detections_days_count(location, num_of_days):
    now = datetime.now()
    days = [(now - timedelta(days=i)).date() for i in range((num_of_days - 1), -1, -1)]

    detections = (
        DetectionRecords.query
        .filter(
            DetectionRecords.location_id == location.id,
            DetectionRecords.datetime >= days[0],
        )
    )

    data_dict = {
        "location": location.location_name,
        "count": detections.count(),
    }
    
    return data_dict
