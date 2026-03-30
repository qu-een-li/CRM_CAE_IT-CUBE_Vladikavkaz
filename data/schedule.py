import sqlalchemy as sq
from .db_session import SqlAlchemyBase


class Schedule(SqlAlchemyBase):
    __tablename__ = 'schedule'
    id = sq.Column(sq.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    group_id = sq.Column(sq.Integer, sq.ForeignKey(
        'groups.id'), nullable=False)
    date = sq.Column(sq.Date, nullable=False)
    start_time = sq.Column(sq.Time, nullable=False)
    end_time = sq.Column(sq.Time, nullable=False)
