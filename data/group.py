import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = "groups"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_of_group = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    direction_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("directions.id"), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    group_type = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.Enum("семестровый", "интенсив", "мастер-класс"),
                                   nullable=False)
    level_of_group = sqlalchemy.Column(sqlalchemy.String,
                                       sqlalchemy.Enum("вводный", "углубленный", "проектный"),
                                       nullable=False)
    study_period_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("study_periods.id"), nullable=False)
    auditorium_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("auditoriums.id"), nullable=True)

    # после выбора типа группы это ьудет только для семестровых и только для мастер-классов
    start_time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    end_time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)

    first_lesson_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    add_days = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)


    study_period = orm.relationship("Study_period")
    teacher = orm.relationship('Teacher')
    direction = orm.relationship("Direction")
    auditorium = orm.relationship("Auditorium")
    students = orm.relationship("Student_in_Group", back_populates="group")
    schedule = orm.relationship("Schedule", back_populates="group", cascade="all, delete-orphan") # если будет отменена группа, то и расписание отменится
