import sqlalchemy as sq
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from datetime import datetime, date


class Schedule(SqlAlchemyBase):
    __tablename__ = 'schedule'
    id = sq.Column(sq.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    group_id = sq.Column(sq.Integer, sq.ForeignKey(
        'groups.id'), nullable=False)
    date = sq.Column(sq.Date, nullable=False)
    start_time = sq.Column(sq.Time, nullable=False)
    end_time = sq.Column(sq.Time, nullable=False)
    group = orm.relationship('Group', back_populates='schedules')

    def is_schedule_at_date(self, cur_date: datetime):
        date_of_schedule = self.date
        date_of_schedule: date
        period_type = self.group.study_period.reporting_period
        if period_type == 'week':
            return cur_date.weekday() == date_of_schedule.weekday()
        if period_type == 'single':
            return date_of_schedule == cur_date.date()
        if period_type == 'year':
            return cur_date.month == date_of_schedule.month and cur_date.day == date_of_schedule.day
        return False
