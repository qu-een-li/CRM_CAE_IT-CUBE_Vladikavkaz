from flask_wtf import FlaskForm
from wtforms import SubmitField, DateTimeLocalField, TimeField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange
from wtforms.fields import TimeField as WTFormsTimeField
from datetime import time


class FlexibleTimeField(WTFormsTimeField):
    def process_formdata(self, valuelist):
        if valuelist:
            # Берем первое НЕПУСТОЕ значение из списка
            value = None
            for v in valuelist:
                if isinstance(v, str) and v.strip():
                    value = v.strip()
                    break

            if not value:
                self.data = None
                return

            try:
                parts = value.split(':')
                if len(parts) == 2:
                    h, m = map(int, parts)
                    self.data = time(h, m, 0)  # Всегда 0 секунд
                elif len(parts) == 3:
                    h, m, s = map(int, parts)
                    self.data = time(h, m, s)
                else:
                    self.data = None
            except (ValueError, TypeError):
                self.data = None
        else:
            self.data = None


def strip_filter(value):
    if isinstance(value, str) and not value.strip():
        return None
    return value


class AddScheduleForm(FlaskForm):
    group = SelectField('Группа', validators=[DataRequired()])

    frequency = SelectField('Периодичность',
                            choices=[
                                ('single', 'Единичное занятие'),
                                ('week', 'Еженедельно'),
                                ('month', 'Ежемесячно'),
                                ('year', 'Ежегодно')
                            ],
                            validators=[DataRequired()])

    datetime = DateTimeLocalField(
        'Дата и время начала', validators=[Optional()])

    weekday = SelectField('День недели',
                          choices=[
                              (0, 'Понедельник'), (1, 'Вторник'), (2, 'Среда'),
                              (3, 'Четверг'), (4, 'Пятница'), (5,
                                                               'Суббота'), (6, 'Воскресенье')
                          ],
                          validators=[Optional()], coerce=int)

    day_of_month = IntegerField('День месяца', validators=[
                                Optional(), NumberRange(min=1, max=31)])

    # Используем наше кастомное поле
    start_time = FlexibleTimeField('Время начала', validators=[
                                   Optional()], filters=[strip_filter], render_kw={"step": "60"})

    submit = SubmitField('Добавить')
