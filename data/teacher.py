import datetime
import sqlalchemy
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase
from datetime import date
from data.parents_for_models import DictConvertable


class Teacher(SqlAlchemyBase, DictConvertable):
    """Таблица с данными об учителе"""

    __tablename__ = "teachers"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    birthday = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    personal_photos = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="anonymous.jpg")

    contests = relationship("Teacher_in_Contests", back_populates="name_teacher")
    qualifications = relationship("TeacherQualification", back_populates="teacher")