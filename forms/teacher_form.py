from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, EmailField, BooleanField, FloatField
from wtforms.validators import DataRequired, Email, Regexp, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed


class TeacherForm(FlaskForm):
    surename = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    patronymic = StringField("Отчество", validators=[Optional()])

    phone = StringField(
        "Телефон",
        validators=[DataRequired(), Regexp(r"^\+7 \d{3} \d{3}-\d{2}-\d{2}$", message="Формат: +7 XXX XXX-XX-XX")],
    )

    email = EmailField("Email", validators=[DataRequired(), Email(message="Введите корректный email адрес")])
    birthday = StringField("Дата рождения", validators=[DataRequired()])

    category = SelectField(
        "Категория",
        choices=[("без категории", "Без категории"), ("1 категория", "1 категория"), ("высшая категория", "Высшая категория")],
        default="без категории",
        validators=[DataRequired()]
    )

    rate = FloatField(
        "Ставка",
        validators=[DataRequired(), NumberRange(min=0, max=1.5, message="Ставка должна быть от 0 до 1.5")],
        default=1.0
    )

    work_condition = SelectField(
        "Условия работы",
        choices=[("основное место работы", "Основное место работы"), ("совместительство", "Совместительство")],
        default="основное место работы",
        validators=[DataRequired()]
    )

    experience_start = StringField("Дата начала педагогической деятельности", validators=[DataRequired()])
    hire_date = StringField("Дата приема на работу", validators=[DataRequired()])
    graduation_date = StringField("Дата завершения обучения в ВУЗе", validators=[Optional()])

    photo = FileField(
        "Фотография",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif"], "Разрешены только изображения!")],
    )

    allow_login = BooleanField("Разрешить вход в систему", default=False)
    user_name = StringField("Имя пользователя для входа в систему")
    password = StringField("Пароль для входа в систему")
    submit = SubmitField("Добавить наставника")