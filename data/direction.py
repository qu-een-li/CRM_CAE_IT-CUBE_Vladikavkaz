import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm, text
from data.parents_for_models import DictConvertable


class Direction(SqlAlchemyBase, DictConvertable):
    """Таблица направлений"""

    __tablename__ = "directions"
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    groups = orm.relationship("Group", back_populates="direction")
    icon_bootstrap = sqlalchemy.Column(
        sqlalchemy.String, nullable=False, server_default=text("'bi-code-slash'"))

    @staticmethod
    def init_data(db_session):
        from data.base_values import load_base_values

        for d in load_base_values()["directions"]:
            if not db_session.query(Direction).filter_by(name=d["name"]).first():
                direction = Direction(name=d["name"], icon_bootstrap=d.get("icon") or "bi-code-slash")
                db_session.add(direction)
        db_session.commit()
