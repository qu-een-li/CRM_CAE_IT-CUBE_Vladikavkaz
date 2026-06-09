import sqlalchemy as sq
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship
from datetime import datetime


class Notification(SqlAlchemyBase):
    """Таблица для уведомлений"""
    __tablename__ = "notifications"
    id = sq.Column(sq.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey(
        "users.id"), nullable=False)
    date = sq.Column(sq.Date, nullable=False, default=datetime.now)
    title = sq.Column(sq.String, default='...')
    body = sq.Column(sq.String, default='Не указано название сообщения')
    is_read = sq.Column(sq.Boolean, default=False)
