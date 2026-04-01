import sqlalchemy
from .db_session import SqlAlchemyBase


class Student_in_Contest(SqlAlchemyBase):
    __tablename__ = "students_in_contests"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("students.id"), nullable=False)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    id_contest = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("contests.id", nullable=False))
    result = sqlalchemy.Column(sqlalchemy.Enum("участник", "призер", "победитель"), nullable=False)
    link_to_document = sqlalchemy.Column(sqlalchemy.String, nullable=False)