from app import app
from flask import render_template, request, redirect, flash
from config import KEY_CSRF
from forms.registrationform import RegistrationForm
from data import db_session
from data.student import Student
from datetime import datetime
from api.api_cities import get_cities_data
from api.api_schools import get_schools_data


@app.route("/students", methods=["GET"])
def students():
    session = db_session.create_session()
    students = session.query(Student).all()
    return render_template("students.html", students=students)


@app.route("/add", methods=["POST", "GET"])
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

        city_title = next(
            (city["title"] for city in get_cities_data(int(form.region.data)) if str(city["id"]) == form.city.data), ""
        )
        school_title = next(
            (
                school["title"]
                for school in get_schools_data(int(form.city.data))
                if str(school["id"]) == form.school.data
            ),
            "",
        )

        user = Student(
            name_student=form.name_student.data,
            name_parent=form.name_parent.data,
            birthday=form.birthday.data,
            PFDO=form.PFDO.data,
            document=form.document.data,
            city=city_title,
            school=school_title,
            parent_phone=form.parent_phone.data,
            student_phone=form.student_phone.data,
            school_class=form.school_class.data,
            adres_of_living=form.adres_of_living.data,
        )
        user.birthday = datetime.strptime(form.birthday.data, "%d.%m.%Y").date()

        session.add(user)
        session.commit()
        flash("Ученик успешно зарегистрирован", "success")
        return redirect("/add")
    return render_template("registration.html", form=form)


@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    db_sess = db_session.create_session()
    student = db_sess.query(Student).get(student_id)

    if not student:
        return redirect("/students")

    form = RegistrationForm(obj=student)

    curr_city = student.city
    curr_school = student.school

    if form.validate_on_submit():
        form.populate_obj(student)
        city_title = next(
            (city["title"] for city in get_cities_data(int(form.region.data)) if str(city["id"]) == form.city.data), ""
        )
        school_title = next(
            (
                school["title"]
                for school in get_schools_data(int(form.city.data))
                if str(school["id"]) == form.school.data
            ),
            "",
        )

        student.city = city_title
        student.school = school_title
        db_sess.commit()
        return redirect("/students")

    if request.method == "POST":
        update_student = Student(
            id=student_id,
            name_student=form.name_student.data,
            name_parent=form.name_parent.data,
            PFDO=form.PFDO.data,
            city=student.city,
            school=student.school,
            student_phone=form.student_phone.data,
            parent_phone=form.parent_phone.data,
            school_class=form.school_class.data,
            document=form.document.data,
            adres_of_living=form.adres_of_living.data,
        )
        update_student.birthday = datetime.strptime(form.birthday.data, "%d.%m.%Y").date()
        db_sess.delete(student)
        db_sess.add(update_student)
        db_sess.commit()
        return redirect("/students")

    return render_template(
        "edit_student.html", form=form, student_id=student_id, current_city=curr_city, current_school=curr_school
    )
