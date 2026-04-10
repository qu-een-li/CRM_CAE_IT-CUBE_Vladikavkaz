import sqlalchemy
from .db_session import SqlAlchemyBase


class Auditorium(SqlAlchemyBase):
    __tablename__ = "auditoriums"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    @staticmethod
    def init_data(db_session):
        auditoriums = ["Программирование на Python", "VR/AR разработка", "Системное администрирование",
                       "Мобильная разработка", "Программирование роботов", "Основы логики и алгоритмики"]

        for name in auditoriums:
            if not db_session.query(Auditorium).filter_by(name=name).first():
                aud = Auditorium(name=name)
                db_session.add(aud)
        db_session.commit()
