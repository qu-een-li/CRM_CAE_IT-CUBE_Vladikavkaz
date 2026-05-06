import sqlalchemy as sq
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from datetime import datetime, date, time
from api.api_base import api_request, to_date, to_int, to_str, to_time, to_bool
from data.group import Group


class Schedule(SqlAlchemyBase):
    __tablename__ = "schedule"
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True, nullable=False)
    group_id = sq.Column(sq.Integer, sq.ForeignKey("groups.id"), nullable=False)
    date = sq.Column(sq.Date, nullable=False)
    start_time = sq.Column(sq.Time, nullable=False)
    end_time = sq.Column(sq.Time, nullable=False)
    group = orm.relationship("Group", back_populates="schedules")
    auditorium_id = sq.Column(sq.Integer, sq.ForeignKey("auditoriums.id"), nullable=True)

    is_cancelled = sq.Column(sq.Boolean, default=False)
    reason_cancel = sq.Column(sq.String, nullable=True)
    is_rescheduled = sq.Column(sq.Boolean, default=False)
    rescheduled_to_date = sq.Column(sq.Date, nullable=True)

    def is_schedule_at_date(self, cur_date: datetime):
        date_of_schedule = self.date
        date_of_schedule: date
        # period_type = self.group.study_period.reporting_period
        # if period_type == "week":
        return cur_date.weekday() == date_of_schedule.weekday()
        # if period_type == "single":
        # return date_of_schedule == cur_date.date()
        # if period_type == "year":
        #     return cur_date.month == date_of_schedule.month and cur_date.day == date_of_schedule.day
        return False

    def to_dict(self):
        return {
            c.name: (
                atr.isoformat()
                if (atr := getattr(self, c.name)) is not None and isinstance(atr, (date, datetime, time))
                else atr
            )
            for c in self.__table__.columns
        }

    @staticmethod
    def from_dict(data_linked: dict):
        data = data_linked.copy()
        """Создает объект Schedule из словаря"""
        # Извлекаем даты и время, если они есть в строковом формате
        if isinstance((date_str := data.get("date")), str):
            data["date"] = date.fromisoformat(date_str)

        if isinstance((start_time := data.get("start_time")), str):
            data["start_time"] = datetime.strptime(start_time, "%H:%M:%S").time()

        if isinstance((end_time := data.get("end_time")), str):
            data["end_time"] = datetime.strptime(end_time, "%H:%M:%S").time()

        if isinstance((rescheduled_to_date := data.get("rescheduled_to_date")), str):
            data["rescheduled_to_date"] = date.fromisoformat(rescheduled_to_date)
        dic = {k: v for k, v in data.items() if k in Schedule.__table__.columns.keys()}
        dic["group"] = Group.from_dict(api_request(f"api/v1/groups/{int(data['group_id'])}"))
        # Создаем объект, отфильтровав ключи, которых нет в модели
        return Schedule(**dic)

    rules = {
        "id": to_int,
        "group_id": to_int,
        "auditorium_id": to_int,
        "date": to_date,
        "start_time": to_time,
        "end_time": to_time,
        "is_cancelled": to_bool,
        "is_rescheduled": to_bool,
        "rescheduled_to_date": to_date,
        "reason_cancel": to_str,  # Просто для полноты картины
    }

    processed = {}
    for key, value in data.items():
        if key in rules:
            try:
                processed[key] = rules[key](value)
            except Exception:
                processed[key] = None  # Или вызывайте abort(), если данные критичны
        else:
            # Если поля нет в правилах, оставляем как есть
            processed[key] = value

    return processed
