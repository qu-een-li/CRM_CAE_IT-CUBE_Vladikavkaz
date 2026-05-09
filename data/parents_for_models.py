from datetime import time, date, datetime
from flask import abort


class DictConvertable:
    def to_dict(self, *fields):
        """Преобразует объект модели SQLALCHEMY в словарь. Если переданы fields, возвращает только их."""
        columns = [
            c for c in self.__table__.columns if not fields or c.name in fields]

        return {
            c.name: (
                atr.isoformat()
                if (atr := getattr(self, c.name)) is not None
                and isinstance(atr, (date, datetime, time))
                else atr
            )
            for c in columns
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Создает объект Модели SQLALCHEMY из словаря, автоматически преобразуя типы: даты, времени, даты-времени и т.д."""
        processed = {}
        # Перебираем все колонки таблицы
        for column in cls.__table__.columns:
            name = column.name

            # Если поле есть во входных данных
            if name in data:
                value = data[name]

                # Если значение — строка, пробуем преобразовать даты/время
                if isinstance(value, str):
                    try:
                        python_type = column.type.python_type

                        if python_type is date:
                            processed[name] = date.fromisoformat(value)
                        elif python_type is time:
                            processed[name] = time.fromisoformat(value)
                        elif python_type is datetime:
                            processed[name] = datetime.fromisoformat(value)
                        else:
                            processed[name] = value
                    except (ValueError, TypeError):
                        abort(400)
                else:
                    processed[name] = value

        # Возвращаем созданный объект класса, распаковывая словарь
        return cls(**processed)
