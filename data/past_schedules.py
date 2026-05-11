import sqlalchemy as sq
from .db_session import SqlAlchemyBase
from data.parents_for_models import DictConvertable
from sqlalchemy.orm import relationship


class PastSchedule(SqlAlchemyBase, DictConvertable):
    """Таблица для определенного прошедшего дня определенного события"""
    __tablename__ = "past_schedules"
    id = sq.Column(sq.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    schedule_id = sq.Column(sq.Integer, sq.ForeignKey(
        "schedules.id"), nullable=False)
    date = sq.Column(sq.Date, nullable=False)
    students = relationship(
        "Student",
        secondary="student_to_past_schedules",
        back_populates="past_schedules"
    )
