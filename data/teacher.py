import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Teacher(SqlAlchemyBase):
    __tablename__ = 'teachers'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)

