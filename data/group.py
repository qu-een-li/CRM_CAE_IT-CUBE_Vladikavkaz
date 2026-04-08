import datetime
import sqlalchemy
from sqlalchemy import orm
from data.student_in_group import student_in_group
from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = "groups"
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_of_group = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    teacher_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    direction_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("directions.id"), nullable=False)
    study_period_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("study_periods.id"), nullable=False)
    level_of_education = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.Enum("вводный", "базовый", "углубленный", "проектный"), nullable=False
    )
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    teacher = orm.relationship('Teacher')
    schedules = orm.relationship('Schedule', back_populates='group')
    study_period = orm.relationship('study_period')
    direction = orm.relationship("Direction", back_populates='groups')
    students = orm.relationship(
        "Student", secondary=student_in_group, back_populates='groups')
