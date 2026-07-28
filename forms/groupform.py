from wtforms import StringField, SelectField, TextAreaField, IntegerField, TimeField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange, Regexp


class GroupForm(FlaskForm):
    name = StringField('Название группы')
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
    auditories = SelectField(
        'Аудитория',
        choices=[('', 'Выберите аудиторию')],
        validators=[DataRequired(message="Пожалуйста, выберите аудиторию из списка.")])
    levels_of_education = SelectField(
        'Глубина знаний',
        choices=[('вводный', 'Вводный'), ('углубленный', 'Углубленный')],)
    description = TextAreaField('Описание предназначения группы')
    duration = TimeField('Длительность занятий', validators=[DataRequired()])
