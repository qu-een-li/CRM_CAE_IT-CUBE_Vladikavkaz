import sqlalchemy as sq
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class Student_to_past_schedule(SqlAlchemyBase):
    __tablename__ = 'student_to_past_schedules'
    id = sq.Column(sq.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    student_id = sq.Column(sq.Integer, sq.ForeignKey(
        'students.id'), nullable=False)
    past_schedule_id = sq.Column(sq.Integer, sq.ForeignKey(
        'past_schedules.id'), nullable=False)
