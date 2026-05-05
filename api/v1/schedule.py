from flask import Blueprint, jsonify
from data.schedule import Schedule
from data import db_session
from api.api_base import require_api_key

schedule_api = Blueprint("schedules", __name__, url_prefix="/api/v1/schedules")


@schedule_api.route("/", methods=["GET"])
@require_api_key
def get_teachers():
    session = db_session.create_session()
    teachers = session.query(Schedule).all()
    return jsonify([teacher.to_dict() for teacher in teachers])
