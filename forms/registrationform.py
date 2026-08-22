from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, IntegerField, SelectField
from wtforms.validators import DataRequired, Regexp

from api.api_regions import get_regions_data
from api.api_cities import get_cities_data
from api.api_schools import get_schools_data


from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired, Regexp, Optional


class RegistrationForm(FlaskForm):
    # Обязательные поля для идентификации
    name_student = StringField('ФИО Ребёнка', validators=[DataRequired()])
    PFDO = IntegerField('ПФДО', validators=[DataRequired()])

    # Поля, которые теперь можно не заполнять (убрали DataRequired)
    name_parent = StringField('ФИО Родителя', validators=[Optional()])
    birthday = StringField('Дата Рождения Ребёнка', validators=[Optional()])
    document = StringField(
        "Документ, удостоверяющий личность", validators=[Optional()])
    parent_phone = StringField('Телефон Родителя', validators=[
        Optional(),
        Regexp(r'^\+7 \d{3} \d{3}-\d{2}-\d{2}$',
               message='Формат: +7 XXX XXX-XX-XX')
    ])
    student_phone = StringField('Телефон Ученика', validators=[
        Optional(),
        Regexp(r'^\+7 \d{3} \d{3}-\d{2}-\d{2}$',
               message='Формат: +7 XXX XXX-XX-XX')
    ])
    school_class = IntegerField('Класс обучения', validators=[Optional()])
    adres_of_living = StringField('Адрес Проживания', validators=[Optional()])

    # Регион, город, школа тоже можно сделать опциональными, но для примера оставим как есть
    # или уберем DataRequired, если нужно.
    region = SelectField('Регион', choices=[], validators=[Optional()])
    city = SelectField('Город', choices=[], validators=[Optional()])
    school = SelectField('Школа', choices=[], validators=[Optional()])

    # Чекбокс для подтверждения статуса кандидата
    confirm_candidate = BooleanField(
        'Я подтверждаю, что ученик будет добавлен как кандидат')

    submit = SubmitField('Зарегистрироваться')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        regions = get_regions_data()
        self.region.choices = [(str(r['id']), r['title']) for r in regions]

        if self.region.data:  # список регионов в json-формате из запроса с помощью url и параметров
            # (это в файле api_schools.py И api_cities.py)
            cities = get_cities_data(int(self.region.data))  # id регионв
            self.city.choices = [(str(c['id']), c['title']) for c in cities]

            if self.city.data:
                schools = get_schools_data(int(self.city.data))  # id города
                self.school.choices = [(str(s['id']), s['title'])
                                       for s in schools]

# ('1086244', 'Республика Северная Осетия — Алания')
