import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Student_in_Group(SqlAlchemyBase):
    __tablename__ = 'students_in_groups'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("groups.id"))
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("students.id"))
