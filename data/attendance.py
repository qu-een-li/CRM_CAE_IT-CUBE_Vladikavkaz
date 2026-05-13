import sqlalchemy as sq
from .db_session import SqlAlchemyBase


class Attendance(SqlAlchemyBase):
    """Таблица посещаемости"""

    __tablename__ = "attendance"
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True, nullable=False)
    student_id = sq.Column(sq.Integer, sq.ForeignKey("students.id"), nullable=False)
    schedule_id = sq.Column(sq.Integer, sq.ForeignKey("schedules.id"), nullable=False)
