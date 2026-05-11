from flask_restful import Resource, abort
from flask import request
from data.past_schedules import PastSchedule
from data.schedule import Schedule
from data.group import Group
from data import db_session
import datetime

from api.api_base import require_api_key


class PastScheduleListResource(Resource):
    # Применит декоратор ко всем методам класса
    method_decorators = [require_api_key]

    def get(self):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            past_schedules = session.query(PastSchedule).all()
            if not past_schedules:
                abort(404, message="Past schedules not found")
            return [item.to_dict(*fields) for item in past_schedules]
        finally:
            session.close()

    def post(self):
        data = request.get_json()
        session = db_session.create_session()
        try:
            # 1. Получаем список всех имен колонок нашей модели
            # Это 'id', 'group_id', 'date', 'start_time' и т.д.
            allowed_columns = {
                column.name: column for column in PastSchedule.__table__.columns}
            filtered_data = {}
            for column_name, value in data.items():
                if isinstance(value, str):
                    try:
                        column = allowed_columns[column_name]
                        python_type = column.type.python_type

                        if python_type is datetime.date:
                            value = datetime.date.fromisoformat(value)
                        elif python_type is datetime.time:
                            value = datetime.time.fromisoformat(value)
                        elif python_type is datetime.datetime:
                            value = datetime.datetime.fromisoformat(value)
                    except (ValueError, TypeError):
                        abort(400)
                if column_name in allowed_columns:
                    filtered_data[column_name] = value
                else:
                    abort(400)
            new_past_schedule = PastSchedule(**filtered_data)

            session.add(new_past_schedule)
            schedule = session.get(Schedule, new_past_schedule.schedule_id)
            group: Group = schedule.group
            students = group.students
            for student in students:
                new_past_schedule.students.append(student)
            session.commit()
            return new_past_schedule.to_dict(), 201

        except Exception as e:
            session.rollback()
            abort(400, message=str(e))
        finally:
            session.close()


class PastScheduleResource(Resource):
    method_decorators = [require_api_key]

    def get(self, past_schedule_id: int):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            schedule = session.query(PastSchedule).get(past_schedule_id)
            if not schedule:
                abort(
                    404, message=f"Past schedule {past_schedule_id} not found")
            return schedule.to_dict(*fields)
        finally:
            session.close()


class StudentsInPastScheduleListResource(Resource):
    method_decorators = [require_api_key]

    def get(self):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            past_schedules = session.query(PastSchedule).all()
            if not past_schedules:
                abort(404, message="Students in past schedule not found")
            return [item.to_dict(*fields) for item in past_schedules]
        finally:
            session.close()
