from flask_wtf import FlaskForm
from wtforms import SubmitField, DateTimeLocalField, TimeField, SelectField
from wtforms.validators import DataRequired, Optional


class AddScheduleForm(FlaskForm):
    group = SelectField('Группа', validators=[DataRequired()])
    datetime = DateTimeLocalField('Дата и время начала',
                                  validators=[DataRequired()])
    duration = TimeField('Длительность', validators=[DataRequired()])
    submit = SubmitField('Добавить')
