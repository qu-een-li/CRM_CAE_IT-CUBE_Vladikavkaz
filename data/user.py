import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from datetime import date
from data.parents_for_models import DictConvertable
from werkzeug.security import generate_password_hash, check_password_hash

import enum
import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from data.parents_for_models import DictConvertable
from flask_login import UserMixin

# 1. Определяем перечисление ролей


class UserRole(enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"


class User(SqlAlchemyBase, DictConvertable, UserMixin):
    """Таблица с данными пользователя для регистрации"""

    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    # Поле роли с использованием Enum
    role = sqlalchemy.Column(sqlalchemy.Enum(UserRole), nullable=False)

    # ID связанной сущности (например, если есть таблица TeacherProfiles)
    id_in_column_of_role = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    # Пароль (обычно String)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    # Имя пользователя
    user_name = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)

    # Дата регистрации (по умолчанию текущее время)
    registration_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<User> {self.id} {self.user_name} ({self.role.value})"

    def set_password(self, password):
        """Создает хеш пароля."""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет пароль на соответствие хешу."""
        return check_password_hash(self.hashed_password, password)
