import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Teacher(SqlAlchemyBase):
    __tablename__ = 'teachers'
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    birthday = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    personal_photos = sqlalchemy.Column(sqlalchemy.String, nullable=False)
