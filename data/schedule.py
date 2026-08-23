import sqlalchemy as sq
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from datetime import datetime, date
from data.parents_for_models import DictConvertable
import enum


class FrequencyType(enum.Enum):
    SINGLE = "single"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class Schedule(SqlAlchemyBase, DictConvertable):
    """Таблица событий - занятия в определенный день и определенное время и с периодичностью повторения."""

    __tablename__ = "schedules"
    id = sq.Column(sq.Integer, primary_key=True,
                   autoincrement=True, nullable=False)
    group_id = sq.Column(sq.Integer, sq.ForeignKey(
        "groups.id"), nullable=False)
    date = sq.Column(sq.Date, nullable=False)
    start_time = sq.Column(sq.Time, nullable=False)
    end_time = sq.Column(sq.Time, nullable=False)
    group = orm.relationship("Group", back_populates="schedules")
    auditorium_id = sq.Column(sq.Integer, sq.ForeignKey(
        "auditoriums.id"), nullable=True)

    is_cancelled = sq.Column(sq.Boolean, default=False)
    reason_cancel = sq.Column(sq.String, nullable=True)
    is_rescheduled = sq.Column(sq.Boolean, default=False)
    rescheduled_to_date = sq.Column(sq.Date, nullable=True)
    frequency = sq.Column(
        sq.Enum(
            FrequencyType,
            # Использовать значения enum, а не имена
            values_callable=lambda x: [e.value for e in x],
            name="frequencytype"
        ),
        default=FrequencyType.SINGLE,
        nullable=False
    )

    def is_schedule_at_date(self, cur_date: datetime) -> bool:
        """Проверяет, проходит ли занятие в указанную дату с учетом периодичности."""
        # Приводим к типу date (убираем время для точного сравнения)
        target_date = cur_date.date() if isinstance(cur_date, datetime) else cur_date
        start_date = self.date

        # Базовая проверка: занятие не может быть раньше даты своего создания
        if target_date < start_date:
            return False

        # Обработка отмен и переносов
        if self.is_cancelled:
            return False

        if self.is_rescheduled:
            return target_date == self.rescheduled_to_date

        # Проверка периодичности через Enum
        if self.frequency == FrequencyType.SINGLE:
            return target_date == start_date

        if self.frequency == FrequencyType.WEEK:
            return target_date.weekday() == start_date.weekday()

        if self.frequency == FrequencyType.MONTH:
            return target_date.day == start_date.day

        if self.frequency == FrequencyType.YEAR:
            return target_date.month == start_date.month and target_date.day == start_date.day

        return False
