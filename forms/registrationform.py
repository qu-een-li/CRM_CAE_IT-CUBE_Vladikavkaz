from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, IntegerField, SelectField
from wtforms.validators import DataRequired

from api.api_regions import get_regions_data
from api.api_cities import get_cities_data
from api.api_schools import get_schools_data



class RegistrationForm(FlaskForm):
    name_parent = StringField('ФИО Родителя', validators=[DataRequired()])
    name_student = StringField('ФИО Ребёнка', validators=[DataRequired()])
    birthday = StringField('Дата Рождения Ребёнка', validators=[DataRequired()])
    document = StringField("Документ, удостоверяющий личность (паспорт/свидетельство о рождении)",
                           validators=[DataRequired()])
    region = SelectField('Регион', choices=[], validators=[DataRequired()])
    city = SelectField('Город', choices=[], validators=[DataRequired()])
    school = SelectField('Школа', choices=[], validators=[DataRequired()])
    PFDO = IntegerField('ПФДО', validators=[DataRequired()])
    parent_phone = StringField('Телефон Родителя', validators=[DataRequired()])
    student_phone = StringField('Телефон Ученика', validators=[DataRequired()])
    school_class = IntegerField('Класс обучения ребёнка', validators=[DataRequired()])
    adres_of_living = StringField('Адрес Проживания', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        regions = get_regions_data()
        self.region.choices = [(str(r['id']), r['title']) for r in regions]

        if self.region.data: #список регионов в json-формате из запроса с помощью url и параметров
            # (это в файле api_schools.py И api_cities.py)
            cities = get_cities_data(int(self.region.data)) #id регионв
            self.city.choices = [(str(c['id']), c['title']) for c in cities]

            if self.city.data:
                schools = get_schools_data(int(self.city.data))#id города
                self.school.choices = [(str(s['id']), s['title']) for s in schools]

#('1086244', 'Республика Северная Осетия — Алания')