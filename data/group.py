import datetime
import sqlalchemy
from sqlalchemy import orm
from data.student_in_group import student_in_group
from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = "groups"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_of_group = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    direction_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("directions.id"), nullable=False)
    study_period_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("study_periods.id"), nullable=False)
    auditorium_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("auditoriums.id"), nullable=True)

    level_of_education = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.Enum("вводный", "базовый", "углубленный"), nullable=False
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
