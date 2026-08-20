import datetime
import sqlalchemy
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase
from datetime import date
from data.parents_for_models import DictConvertable


class Teacher(SqlAlchemyBase, DictConvertable):
    """Таблица с данными об учителе"""

    __tablename__ = "teachers"
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    birthday = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    personal_photos = sqlalchemy.Column(
        sqlalchemy.String, nullable=False, default="anonymous.jpg")

    contests = relationship("Teacher_in_Contests",
                            back_populates="name_teacher")
    qualifications = relationship(
        "TeacherQualification", back_populates="teacher")

    category = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    rate = sqlalchemy.Column(sqlalchemy.Float, nullable=True, default=1.0)
    experience_start = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    graduation_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    work_condition = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hire_date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    dismissal_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)

    def get_formatted_teachers_patronymic(self):
        formatted_teacher_name = f"{self.surename} {self.name[0]}.{self.patronymic[0]}.".title(
        )
        return formatted_teacher_name

    def get__teachers_patronymic(self):
        formatted_teacher_name = f"{self.surename} {self.name} {self.patronymic}".title(
        )
        return formatted_teacher_name

    def get_experience(self):
        """Рассчитывает стаж работы"""
        if not self.experience_start:
            return "Нет данных"

        today = date.today()
        years = today.year - self.experience_start.year
        months = today.month - self.experience_start.month
        if months < 0:
            years -= 1
            months += 12
        elif months == 0 and today.day < self.experience_start.day:
            years -= 1
            months = 11

        if 11 <= years % 100 <= 14:
            year_word = "л."
        elif years % 10 == 1:
            year_word = "г."
        elif 2 <= years % 10 <= 4:
            year_word = "г."
        else:
            year_word = "л."

        if years == 0:
            if months == 0:
                days = (today - self.experience_start).days
                if days < 30:
                    return f"{days} дн."
                else:
                    return f"{months} мес."
            return f"{months} мес."

        if months > 0:
            return f"{years} {year_word} {months} мес."
        else:
            return f"{years} {year_word}"
