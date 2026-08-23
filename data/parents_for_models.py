from datetime import time, date, datetime
from flask import abort
import enum
from sqlalchemy import Enum as SAEnum


class DictConvertable:
    """Класс родитель для преобразования таблицы sqlalchemy в словарь и получения из словаря обьекта таблицы."""

    def to_dict(self, *fields):
        """Преобразует объект модели SQLALCHEMY в словарь. Если переданы fields, возвращает только их."""
        columns = [
            c for c in self.__table__.columns if not fields or c.name in fields]

        result = {}
        for c in columns:
            value = getattr(self, c.name)

            if value is None:
                result[c.name] = None
            # Обработка Enum
            elif isinstance(value, enum.Enum):
                # Берем значение, а не объект Enum
                result[c.name] = value.value
            # Обработка дат
            elif isinstance(value, (date, datetime, time)):
                result[c.name] = value.isoformat()
            else:
                result[c.name] = value

        return result

    @classmethod
    def from_dict(cls, data: dict):
        """Создает объект Модели SQLALCHEMY из словаря, автоматически преобразуя типы."""
        processed = {}

        for column in cls.__table__.columns:
            name = column.name
            if name not in data:
                continue

            value = data[name]
            if value is None:
                processed[name] = None
                continue

            # Определяем тип колонки
            column_type = column.type

            # Проверяем, является ли колонка Enum
            if isinstance(column_type, SAEnum):
                # Получаем класс Enum из типа колонки
                enum_class = column_type.enum_class

                if enum_class and isinstance(enum_class, type) and issubclass(enum_class, enum.Enum):
                    # Если value уже является экземпляром Enum
                    if isinstance(value, enum_class):
                        processed[name] = value
                    # Если value - строка
                    elif isinstance(value, str):
                        try:
                            # Пробуем найти по значению (value)
                            for member in enum_class:
                                if member.value == value:
                                    processed[name] = member
                                    break
                            else:
                                # Если не нашли по значению, пробуем по имени
                                processed[name] = enum_class[value]
                        except (KeyError, ValueError):
                            # Если не получилось, оставляем как есть (это вызовет ошибку при создании объекта)
                            processed[name] = value
                    else:
                        processed[name] = value
                else:
                    # Если enum_class не определен, пробуем другие способы
                    processed[name] = value

            # Для дат и времени
            elif column_type.python_type is date:
                if isinstance(value, str):
                    processed[name] = date.fromisoformat(value)
                elif isinstance(value, date):
                    processed[name] = value
                else:
                    processed[name] = value

            elif column_type.python_type is time:
                if isinstance(value, str):
                    processed[name] = time.fromisoformat(value)
                elif isinstance(value, time):
                    processed[name] = value
                else:
                    processed[name] = value

            elif column_type.python_type is datetime:
                if isinstance(value, str):
                    processed[name] = datetime.fromisoformat(value)
                elif isinstance(value, datetime):
                    processed[name] = value
                else:
                    processed[name] = value
            else:
                processed[name] = value

        return cls(**processed)
