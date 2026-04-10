import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from data.student_in_group import student_in_group


class Student(SqlAlchemyBase):
    __tablename__ = 'students'
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_student = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name_parent = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    birthday = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    PFDO = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    school = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    school_class = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    student_phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    parent_phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    document = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    adres_of_living = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    groups = orm.relationship(
        "Group", secondary=student_in_group, back_populates='students')

    def __repr__(self):
        return f'Student("{self.name_student}")'
