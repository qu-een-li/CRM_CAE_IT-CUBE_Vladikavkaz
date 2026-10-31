from wtforms import StringField, SelectField, TextAreaField, DateTimeLocalField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length


class GroupForm(FlaskForm):
    name = StringField(
        'Название группы',
        validators=[DataRequired(message="Введите название группы."), Length(max=100)],
        render_kw={"placeholder": "Пегас, 9-12 лет"})
    teachers = SelectField(
        'Учитель',
        choices=[('', 'Выберите учителя')],
        validators=[DataRequired(message="Пожалуйста, выберите учителя из списка.")])
    directions = SelectField(
        'Направление',
        choices=[('', 'Выберите направление')],
        validators=[DataRequired(message="Пожалуйста, выберите направление из списка.")])
    study_periods = SelectField(
        'Период обучения',
        choices=[('', 'Выберите период обучения')],
        validators=[DataRequired(message="Пожалуйста, выберите период обучения из списка.")])
    # аудитория записывается в событие (первое занятие), а не в группу
    auditories = SelectField(
        'Аудитория',
        choices=[('', 'Выберите аудиторию')],
        validators=[DataRequired(message="Пожалуйста, выберите аудиторию из списка.")])
    levels_of_education = SelectField(
        'Глубина знаний',
        choices=[('вводный', 'Вводный'), ('углубленный', 'Углубленный')],)
    # варианты берутся из base_values.json (страница /settings)
    group_type = SelectField(
        'Тип группы',
        validators=[DataRequired(message="Выберите тип группы.")])
    description = TextAreaField('Описание предназначения группы (требования к обучающимся)')
    # длительность ОДНОГО занятия
    duration = SelectField(
        'Длительность одного занятия',
        choices=[('00:40', '40 мин'), ('01:30', '90 мин')],
        default='01:30',
        validators=[DataRequired(message="Выберите длительность занятия.")])
    start_datetime = DateTimeLocalField(
        'Дата и время начала (первое занятие)',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(message="Укажите дату и время первого занятия.")])
