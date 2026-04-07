from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Regexp, Optional
from flask_wtf.file import FileField, FileAllowed


class TeacherForm(FlaskForm):
    surename = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[Optional()])

    phone = StringField('Телефон', validators=[DataRequired(),
        Regexp(r'^\+7 \d{3} \d{3}-\d{2}-\d{2}$', message='Формат: +7 XXX XXX-XX-XX')])

    email = EmailField('Email', validators=[DataRequired(), Email(message='Введите корректный email адрес')])
    birthday = StringField('Дата рождения', validators=[DataRequired()])
    status = StringField('Статус', validators=[DataRequired()])

    photo = FileField('Фотография', validators=[Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Разрешены только изображения!')])

    submit = SubmitField('Добавить наставника')
