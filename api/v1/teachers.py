from flask_restful import Resource, abort
from data.teacher import Teacher
from data import db_session
from api.api_base import require_api_key
from flask import request


class TeacherListResource(Resource):
    # Применит декоратор ко всем методам класса
    method_decorators = [require_api_key]

    def get(self):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            teachers = session.query(Teacher).all()
            if not teachers:
                abort(404, message="Teacher not found")
            return [item.to_dict(*fields) for item in teachers]
        finally:
            session.close()


class TeacherResource(Resource):
    method_decorators = [require_api_key]

    def get(self, teacher_id: int):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            teacher = session.query(Teacher).get(teacher_id)
            if not teacher:
                abort(404, message=f" Teacher {teacher_id} not found")
            return teacher.to_dict(*fields)
        finally:
            session.close()
