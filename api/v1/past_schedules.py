from flask_restful import Resource, abort
from flask import request
from data.past_schedules import PastSchedule
from data.students_to_past_schedule import Student_to_past_schedule
from data.schedule import Schedule
from data.group import Group
from data import db_session
import datetime
from datetime import date

from api.api_base import require_api_key


class PastScheduleListResource(Resource):
    # Применит декоратор ко всем методам класса
    method_decorators = [require_api_key]

    def get(self):
        fields = request.args.getlist("fields")
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
        print(data)
        session = db_session.create_session()
        try:
            # 1. Получаем список всех имен колонок нашей модели
            # Это 'id', 'group_id', 'date', 'start_time' и т.д.
            allowed_columns = {column.name: column for column in PastSchedule.__table__.columns}
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
                        print("Не позволительный тип данных")
                        abort(400)
                if column_name in allowed_columns:
                    filtered_data[column_name] = value
                else:
                    print("Не позволительные данные")
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
            print(e)
            session.rollback()
            abort(400, message=str(e))
        finally:
            session.close()


class PastScheduleResource(Resource):
    method_decorators = [require_api_key]

    def get(self, past_schedule_id: int):
        fields = request.args.getlist("fields")
        session = db_session.create_session()
        try:
            schedule = session.query(PastSchedule).get(past_schedule_id)
            if not schedule:
                abort(404, message=f"Past schedule {past_schedule_id} not found")
            return schedule.to_dict(*fields)
        finally:
            session.close()


class PastScheduleFromScheduleAndDateResource(Resource):
    method_decorators = [require_api_key]

    def get(self, schedule_id: int, date_str: str):
        formatted_date = date.fromisoformat(date_str)
        fields = request.args.getlist("fields")

        session = db_session.create_session()
        try:
            # Ищем запись, где совпадают оба поля: schedule_id и date
            schedule = session.query(PastSchedule).filter_by(schedule_id=schedule_id, date=formatted_date).first()

            if not schedule:
                abort(404, message=f"Past schedule for schedule {schedule_id} on {date_str} not found")

            return schedule.to_dict(*fields)
        finally:
            session.close()


class StudentsInPastScheduleResource(Resource):
    method_decorators = [require_api_key]

    def get(self, past_schedule_id: int):
        fields = request.args.getlist("fields")
        add_fields = request.args.getlist("add_fields")
        session = db_session.create_session()
        try:
            past_schedule = session.query(PastSchedule).get(past_schedule_id)
            students = past_schedule.students
            if not students:
                abort(404, message="Students in past schedule not found")
            ans = [item.to_dict(*fields) for item in students]
            if "were_present" in add_fields:
                for student_dict in ans:
                    were_present = (
                        session.query(Student_to_past_schedule)
                        .filter_by(student_id=student_dict["id"], past_schedule_id=past_schedule_id)
                        .first()
                    ).were_present
                    student_dict["were_present"] = were_present
            return ans
        finally:
            session.close()


class StudentInPastScheduleResource(Resource):
    method_decorators = [require_api_key]

    def put(self, past_schedule_id: int, student_id: int):
        data = request.get_json()
        session = db_session.create_session()
        try:
            student_to_past_schedule = (
                session.query(Student_to_past_schedule)
                .filter_by(student_id=student_id, past_schedule_id=past_schedule_id)
                .first()
            )
            if not student_to_past_schedule:
                abort(404, message="Students in past schedule or past schedule not found")
            if "were_present" in data:
                student_to_past_schedule.were_present = data["were_present"]
            session.commit()
            return student_to_past_schedule.to_dict(), 201
        finally:
            session.close()
