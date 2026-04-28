import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Teacher_in_Contests(SqlAlchemyBase):
    __tablename__ = "teachers_in_contests"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    contest_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("contests_for_teachers.id"), nullable=False)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    end_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    place = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    rank = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    name_contest = relationship("Contest_for_Teachers", back_populates="teachers")
    name_teacher = relationship("Teacher", back_populates="contests")
