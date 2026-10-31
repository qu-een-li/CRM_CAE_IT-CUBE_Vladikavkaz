import sqlalchemy
from .db_session import SqlAlchemyBase


class Auditorium(SqlAlchemyBase):
    """Таблица аудиторий/кабинетов"""

    __tablename__ = "auditoriums"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    @staticmethod
    def init_data(db_session):
        from data.base_values import load_base_values

        for name in load_base_values()["auditoriums"]:
            if not db_session.query(Auditorium).filter_by(name=name).first():
                aud = Auditorium(name=name)
                db_session.add(aud)
        db_session.commit()
