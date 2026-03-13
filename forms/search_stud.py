from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional

from api.api_regions import get_regions_data
from api.api_cities import get_cities_data
from api.api_schools import get_schools_data


class SearchForm(FlaskForm):
    name_parent = StringField('ФИО Родителя', validators=[Optional()])
    name_student = StringField('ФИО Ребёнка', validators=[Optional()])
    birthday = StringField('Дата Рождения Ребёнка', validators=[Optional()])
    document = StringField("Документ, удостоверяющий личность (паспорт/свидетельство о рождении)",
                           validators=[Optional()])
    region = SelectField('Регион', choices=[], validators=[Optional()])
    city = SelectField('Город', choices=[], validators=[Optional()])
    school = SelectField('Школа', choices=[], validators=[Optional()])
    PFDO = IntegerField('ПФДО', validators=[Optional()])
    parent_phone = StringField('Телефон Родителя', validators=[Optional()])
    student_phone = StringField('Телефон Ученика', validators=[Optional()])
    school_class = IntegerField('Класс обучения ребёнка', validators=[Optional()])
    adres_of_living = StringField('Адрес Проживания', validators=[Optional()])
    submit = SubmitField('Поиск')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        regions = get_regions_data()
        self.region.choices = [(str(r['id']), r['title']) for r in regions]

        if self.region.data:  # список регионов в json-формате из запроса с помощью url и параметров
            # (это в файле api_schools.py И api_cities.py)
            cities = get_cities_data(int(self.region.data))  # id регионв
            self.city.choices = [(str(c['id']), c['title']) for c in cities]

            if self.city.data:
                schools = get_schools_data(int(self.city.data))  # id города
                self.school.choices = [(str(s['id']), s['title']) for s in schools]

# ('1086244', 'Республика Северная Осетия — Алания')