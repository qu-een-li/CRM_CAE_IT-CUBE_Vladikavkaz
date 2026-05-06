import datetime
import sqlalchemy
import json
from .db_session import SqlAlchemyBase
from api.api_base import api_request
from datetime import date


class Teacher(SqlAlchemyBase):
    __tablename__ = "teachers"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    birthday = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    personal_photos = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="anonymous.jpg")

    def to_dict(self):
        return {
            c.name: (
                atr.isoformat()
                if (atr := getattr(self, c.name)) is not None and isinstance(atr, (datetime.date))
                else atr
            )
            for c in self.__table__.columns
        }

    @staticmethod
    def from_dict(data_linked: dict):
        data = data_linked.copy()
        """Создает объект Group из словаря"""
        if isinstance((birthday := data.get("birthday")), str):
            data["birthday"] = date.fromisoformat(birthday)

        dic = {k: v for k, v in data.items() if k in Teacher.__table__.columns.keys()}
        return Teacher(**dic)
