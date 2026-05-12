import sqlalchemy
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase


class TeacherQualification(SqlAlchemyBase):
    __tablename__ = 'teacher_qualifications'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"), nullable=False)
    course_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("qualification_courses.id"), nullable=False)
    registration_number = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    issue_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    certificate_number = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    teacher = relationship("Teacher", back_populates="qualifications")
    course = relationship("QualificationCourse", back_populates="teacher_qualifications")