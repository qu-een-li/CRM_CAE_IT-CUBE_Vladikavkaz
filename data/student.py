import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Student(SqlAlchemyBase):
    __tablename__ = 'students'
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_student = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name_parent = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    birthday = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    PFDO = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    school = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    school_class = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    student_phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    parent_phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    document = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    adres_of_living = sqlalchemy.Column(sqlalchemy.String, nullable=True)
