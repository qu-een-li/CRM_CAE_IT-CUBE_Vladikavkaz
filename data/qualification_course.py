import sqlalchemy
from .db_session import SqlAlchemyBase


class QualificationCourse(SqlAlchemyBase):
    __tablename__ = "qualification_courses"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    program_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hours = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    organization = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    place = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)