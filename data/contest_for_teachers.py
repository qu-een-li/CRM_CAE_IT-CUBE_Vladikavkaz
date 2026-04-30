import sqlalchemy
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Contest_for_Teachers(SqlAlchemyBase):
    __tablename__ = "contests_for_teachers"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    end_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    level_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("level_contests.id"), nullable=False)
    organizer = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    level = orm.relationship("Level_contest")
    teachers = relationship("Teacher_in_Contests", back_populates="name_contest")
