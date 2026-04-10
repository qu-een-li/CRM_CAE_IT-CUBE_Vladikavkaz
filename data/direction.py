import sqlalchemy
from .db_session import SqlAlchemyBase


class Direction(SqlAlchemyBase):
    __tablename__ = "directions"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    @staticmethod
    def init_data(db_session):
        directions = [
            "Программирование на Python",
            "Мобильная разработка",
            "VR/AR",
            "Системное администрирование",
            "Основы логики и алгоритмики",
            "Робототехника",
            "Основы компьютерной грамотности",
            "Машинное обучение",
            "3D-моделирование",
            "Яндекс-Лицей"
        ]

        for direction_name in directions:
            if not db_session.query(Direction).filter_by(name=direction_name).first():
                direction = Direction(name=direction_name)
                db_session.add(direction)
        db_session.commit()