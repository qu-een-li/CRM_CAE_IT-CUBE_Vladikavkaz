import sqlalchemy
from .db_session import SqlAlchemyBase


class Contest(SqlAlchemyBase):
    __tablename__ = "contests"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    direction_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("directions.id"), nullable=False)
    link_contest = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    level_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("level_contests.id"), nullable=False)
    contest_organizer = sqlalchemy.Column(sqlalchemy.String, nullable=False)