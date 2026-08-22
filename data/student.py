import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from data.student_in_group import student_in_group
from data.parents_for_models import DictConvertable
from sqlalchemy.orm import relationship


class Student(SqlAlchemyBase, DictConvertable):
    """Таблица с данными ученика."""

    __tablename__ = "students"
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_student = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name_parent = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    birthday = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    PFDO = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    school = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    school_class = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    student_phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    parent_phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    document = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    adres_of_living = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    groups = orm.relationship(
        "Group", secondary=student_in_group, back_populates="students")
    past_schedules = relationship(
        "PastSchedule", secondary="student_to_past_schedules", back_populates="students")
    is_candidate = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    def __repr__(self):
        return f'Student("{self.name_student}")'
