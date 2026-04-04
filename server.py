from flask import Flask, render_template, request, redirect
from config import KEY_CSRF
from forms.registrationform import RegistrationForm
from data import db_session
from data.student import Student
from data.group import Group
from data.teacher import Teacher
from data.schedule import Schedule
from flask_login import LoginManager
from forms.search_stud import SearchForm
from forms.add_schedule import AddScheduleForm
from api.api_regions import regions_api
from api.api_cities import cities_api, get_cities_data
from api.api_schools import schools_api, get_schools_data
from datetime import datetime, timedelta
app = Flask(__name__)
app.config['SECRET_KEY'] = KEY_CSRF

app.register_blueprint(regions_api)
app.register_blueprint(cities_api)
app.register_blueprint(schools_api)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Student).get(user_id)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/students', methods=['GET'])
def students():
    session = db_session.create_session()
    students = session.query(Student).all()
    return render_template("students.html", students=students)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = RegistrationForm()

    if request.method == "POST":
        if "region" in request.form:
            region_id = request.form["region"]
            cities = get_cities_data(int(region_id))
            form.city.choices = [(str(c["id"]), c["title"]) for c in cities]
            form.school.choices = []

        if "city" in request.form:
            city_id = request.form["city"]
            schools = get_schools_data(int(city_id))
            form.school.choices = [(str(s["id"]), s["title"]) for s in schools]

    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(Student).filter(Student.PFDO == form.PFDO.data).first():
            return render_template("registration.html", form=form, message="Такой ученик уже существует")

        city_title = next((city["title"] for city in get_cities_data(int(form.region.data))
                           if str(city["id"]) == form.city.data), "")
        school_title = next((school["title"] for school in get_schools_data(int(form.city.data))
                             if str(school["id"]) == form.school.data), "")

        user = Student(name_student=form.name_student.data, name_parent=form.name_parent.data,
                       birthday=form.birthday.data, PFDO=form.PFDO.data,
                       document=form.document.data,
                       city=city_title,
                       school=school_title, parent_phone=form.parent_phone.data,
                       student_phone=form.student_phone.data, school_class=form.school_class.data,
                       adres_of_living=form.adres_of_living.data)
        session.add(user)
        session.commit()
        return redirect("/add")
    return render_template("registration.html", form=form)


@app.route('/search', methods=['POST', 'GET'])
def search():
    form = SearchForm()
    if request.method == "POST":
        session = db_session.create_session()
        query = session.query(Student)
        if form.name_student.data:
            query = query.filter(Student.name_student.ilike(
                f'%{form.name_student.data}%'))
        if form.name_parent.data:
            query = query.filter(Student.name_parent.ilike(
                f'%{form.name_parent.data}%'))
        if form.birthday.data:
            query = query.filter(Student.birthday == form.birthday.data)
        if form.document.data:
            query = query.filter(
                Student.document.ilike(f'%{form.document.data}%'))
        if form.region.data:
            city_title = next((city["title"] for city in get_cities_data(int(form.region.data))
                               if str(city["id"]) == form.city.data), "")
            query = query.filter(Student.city == city_title)
        if form.school.data:
            school_title = next((school["title"] for school in get_schools_data(int(form.city.data))
                                 if str(school["id"]) == form.school.data), "")
            query = query.filter(Student.school == school_title)
        if form.PFDO.data:
            query = query.filter(Student.PFDO == form.PFDO.data)
        if form.parent_phone.data:
            query = query.filter(Student.parent_phone.ilike(
                f'%{form.parent_phone.data}%'))
        if form.student_phone.data:
            query = query.filter(Student.student_phone.ilike(
                f'%{form.student_phone.data}%'))
        if form.school_class.data:
            query = query.filter(Student.school_class ==
                                 form.school_class.data)
        if form.adres_of_living.data:
            query = query.filter(Student.adres_of_living.ilike(
                f'%{form.adres_of_living.data}%'))
        students = query.all()
        return render_template("students.html", students=students)
    return render_template("search.html", form=form)


@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    db_sess = db_session.create_session()
    student = db_sess.query(Student).get(student_id)

    if not student:
        return redirect('/students')

    form = RegistrationForm(obj=student)

    curr_city = student.city
    curr_school = student.school

    if form.validate_on_submit():
        form.populate_obj(student)
        city_title = next((city["title"] for city in get_cities_data(int(form.region.data))
                           if str(city["id"]) == form.city.data), "")
        school_title = next((school["title"] for school in get_schools_data(int(form.city.data))
                             if str(school["id"]) == form.school.data), "")

        student.city = city_title
        student.school = school_title
        db_sess.commit()
        return redirect('/students')

    if request.method == "POST":
        update_student = Student(id=student_id, name_student=form.name_student.data, name_parent=form.name_parent.data,
                                 birthday=form.birthday.data,
                                 PFDO=form.PFDO.data, city=student.city, school=student.school,
                                 student_phone=form.student_phone.data,
                                 parent_phone=form.parent_phone.data, school_class=form.school_class.data,
                                 document=form.document.data,
                                 adres_of_living=form.adres_of_living.data)
        db_sess.delete(student)
        db_sess.add(update_student)
        db_sess.commit()
        return redirect('/students')

    return render_template("edit_student.html", form=form, student_id=student_id, current_city=curr_city, current_school=curr_school)


def get_full_teachers_initials_by_column(teacher: Teacher):
    return f'{teacher.name} {teacher.patronymic} {teacher.surename}'


@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    form = AddScheduleForm()
    db_sess = db_session.create_session()
    form.group.choices = [(group.id, f'"{group.name_of_group}" c {get_full_teachers_initials_by_column(group.teacher)}')
                          for group in db_sess.query(Group).all()]
    if form.validate_on_submit():
        is_there_problem = False
        schedule = Schedule()
        schedule.group_id = int(form.group.data)
        schedule.date = form.datetime.data.date()
        dt = form.datetime.data
        duration = timedelta(hours=form.duration.data.hour,
                             minutes=form.duration.data.minute)
        end_dt = duration + dt
        schedule.start_time = dt.time()
        schedule.end_time = end_dt.time()
        print(dt.hour * 60 + dt.minute + duration.seconds / 60)
        # проверка, что занятие кончиться в тот же день когда и началось
        if dt.hour * 60 + dt.minute + duration.seconds / 60 >= 24 * 60:
            form.duration.errors.append(
                "the lesson may not start and end on different days")
            is_there_problem = True
        if not is_there_problem:
            db_sess.add(schedule)
            db_sess.commit()
    return render_template('add_schedule.html', form=form)


if __name__ == '__main__':
    db_session.global_init("db/reg_form.db")
    app.run(port=8080, host='127.0.0.1')
