import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = 'groups'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_of_group = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"))
    study_period_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("study_periods.id"))



