import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = "groups"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_of_group = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    study_period_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("study_periods.id"), nullable=False)
    level_of_education = sqlalchemy.Column(
        sqlalchemy.String, sqlalchemy.Enum("вводный", "базовый", "углубленный", "проектный"), nullable=False
    )
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    teacher = orm.relationship('Teacher')