import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

from .db_session import SqlAlchemyBase


class Study_period(SqlAlchemyBase):
    __tablename__ = 'study_periods'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    reporting_period = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    date_start = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    date_end = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
