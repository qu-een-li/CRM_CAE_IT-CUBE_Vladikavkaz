import sqlalchemy as sq
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Schedule(SqlAlchemyBase):
    __tablename__ = 'schedule'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True, nullable=False)
    group_id = sq.Column(sq.Integer, sq.ForeignKey('groups.id'), nullable=False)
    date = sq.Column(sq.Date, nullable=False)
    start_time = sq.Column(sq.Time, nullable=False)
    end_time = sq.Column(sq.Time, nullable=False)
    auditorium_id = sq.Column(sq.Integer, sq.ForeignKey("auditoriums.id"), nullable=True)

    is_cancelled = sq.Column(sq.Boolean, default=False)
    reason_cancel = sq.Column(sq.String, nullable=True)
    is_rescheduled = sq.Column(sq.Boolean, default=False)
    rescheduled_to_date = sq.Column(sq.Date, nullable=True)

    # group = orm.relationship("Group", back_populates="schedule")
    # auditorium = orm.relationship("Auditorium")
    # attendances = orm.relationship("Attendance", back_populates="schedule",
    #                                cascade="all, delete-orphan")  # если бдует отменено занятие, то и посещаемость аннулируется
