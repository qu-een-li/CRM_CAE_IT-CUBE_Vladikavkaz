import sqlalchemy as sq
from .db_session import SqlAlchemyBase


class Attendance(SqlAlchemyBase):
    __tablename__ = 'attendance'
    id = sq.Column(sq.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    students_in_groups_id = sq.Column(
        sq.Integer, sq.ForeignKey('students.id'), nullable=False)
    schedule_id = sq.Column(sq.Integer, sq.ForeignKey(
        'schedule.id'), nullable=False)
