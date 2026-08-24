import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Student_in_Contest(SqlAlchemyBase):
    """Таблица связывающая студенита, учителя и конкурс c их исходом и ссылкой на сертификат"""

    __tablename__ = "students_in_contests"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("students.id"), nullable=False)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    id_contest = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("contests.id"), nullable=False)
    result = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="участник")
    link_to_document = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    student = relationship("Student", foreign_keys=[student_id], backref="student_contests")
    teacher = relationship("Teacher", foreign_keys=[teacher_id], backref="teacher_student_contests")
    contest = relationship("Contest", foreign_keys=[id_contest], backref="student_contests")