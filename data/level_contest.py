import sqlalchemy
from .db_session import SqlAlchemyBase


class Level_contest(SqlAlchemyBase):
    __tablename__ = "level_contests"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    @staticmethod
    def init_data(db_session):
        levels = [
            "Внутреннее мероприятие",
            "Муниципальный/региональный уровень, открытый конкурс",
            "Межрегиональный уровень",
            "Федеральный уровень",
            "Международный уровень"
        ]

        for level_name in levels:
            if not db_session.query(Level_contest).filter_by(name=level_name).first():
                level = Level_contest(name=level_name)
                db_session.add(level)
        db_session.commit()