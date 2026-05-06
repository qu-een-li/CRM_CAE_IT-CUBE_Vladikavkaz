import datetime
import sqlalchemy
from sqlalchemy import orm
from data.student_in_group import student_in_group
from data.teacher import Teacher

from .db_session import SqlAlchemyBase
import json
from api.api_base import api_request


class Group(SqlAlchemyBase):
    __tablename__ = "groups"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_of_group = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    direction_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("directions.id"), nullable=False)
    study_period_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("study_periods.id"), nullable=False)
    auditorium_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("auditoriums.id"), nullable=True)

    level_of_education = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.Enum("вводный", "углубленный", "проектный"), nullable=False
    )
    group_type = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.Enum("семестровый", "интенсив", "мастер-класс"), nullable=False
    )

    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    teacher = orm.relationship("Teacher")
    schedules = orm.relationship("Schedule", back_populates="group")
    study_period = orm.relationship("Study_period")
    direction = orm.relationship("Direction", back_populates="groups")
    students = orm.relationship("Student", secondary=student_in_group, back_populates="groups")
    # после выбора типа группы это ьудет только для семестровых и только для мастер-классов

    first_lesson_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    add_days = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    # auditorium = orm.relationship("Auditorium")
    # schedule = orm.relationship("Schedule", back_populates="group", cascade="all, delete-orphan") # если будет отменена группа, то и расписание отменится

    def to_dict(self):
        return {
            c.name: (
                atr.isoformat()
                if (atr := getattr(self, c.name)) is not None and isinstance(atr, (datetime.datetime, datetime.time))
                else atr
            )
            for c in self.__table__.columns
        }

    @staticmethod
    def from_dict(data_linked: dict):
        data = data_linked.copy()
        """Создает объект Group из словаря"""
        if isinstance((add_days := data.get("add_days")), str):
            try:
                data["add_days"] = json.loads(add_days)
            except json.JSONDecodeError:
                pass

        if isinstance((duration := data.get("duration")), str):
            try:
                data["duration"] = datetime.datetime.strptime(duration, "%H:%M:%S").time()
            except ValueError:
                data["duration"] = datetime.datetime.strptime(duration, "%H:%M").time()

        if isinstance((first_lesson_date := data.get("first_lesson_date")), str):
            data["first_lesson_date"] = datetime.datetime.strptime(first_lesson_date, "%Y-%m-%d").date()
        dic = {k: v for k, v in data.items() if k in Group.__table__.columns.keys()}
        dic["teacher"] = Teacher.from_dict(api_request(f"api/v1/teachers/{dic['teacher_id']}"))
        return Group(**dic)
