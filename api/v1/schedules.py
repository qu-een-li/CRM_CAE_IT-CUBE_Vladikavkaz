from flask_restful import Resource, abort
from flask import request
from data.schedule import Schedule
from data import db_session
import datetime

from api.api_base import require_api_key


class ScheduleListResource(Resource):
    method_decorators = [require_api_key]  # Применит декоратор ко всем методам класса

    def get(self):
        session = db_session.create_session()
        try:
            schedules = session.query(Schedule).all()
            if not schedules:
                abort(404, message="Groups not found")
            return [item.to_dict() for item in schedules]
        finally:
            session.close()


class ScheduleResource(Resource):
    method_decorators = [require_api_key]

    def get(self, schedule_id: int):
        session = db_session.create_session()
        try:
            schedule = session.query(Schedule).get(schedule_id)
            if not schedule:
                abort(404, message=f"Schedule {schedule_id} not found")
            return schedule.to_dict()
        finally:
            session.close()

    def post(self):
        data = request.get_json()
        session = db_session.create_session()

        try:
            # 1. Получаем список всех имен колонок нашей модели
            # Это 'id', 'group_id', 'date', 'start_time' и т.д.
            allowed_columns = Schedule.__table__.columns.keys()

            # 2. Оставляем в data только те ключи, которые есть в таблице
            filtered_data = {key: value for key, value in data.items() if key in allowed_columns}

            # 3. Конвертируем даты (если они есть в отфильтрованных данных)
            if "date" in filtered_data:
                filtered_data["date"] = datetime.strptime(filtered_data["date"], "%Y-%m-%d").date()
            if "date" in filtered_data:
                filtered_data["date"] = datetime.datetime.fromisoformat(filtered_data["date"])

            if "start_time" in filtered_data:
                filtered_data["start_time"] = datetime.strptime(filtered_data["start_time"], "%H:%M:%S").time()
            if "end_time" in filtered_data:
                filtered_data["end_time"] = datetime.strptime(filtered_data["end_time"], "%H:%M:%S").time()

            new_schedule = Schedule(**filtered_data)

            session.add(new_schedule)
            session.commit()
            return new_schedule.to_dict(), 201

        except Exception as e:
            session.rollback()
            abort(400, message=str(e))
        finally:
            session.close()
