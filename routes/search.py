from app import app
from flask import render_template, request
from forms.search_stud import SearchForm
from data import db_session
from data.student import Student
from api.api_cities import get_cities_data
from api.api_schools import get_schools_data
from datetime import datetime


@app.route("/search", methods=["POST", "GET"])
def search():
    form = SearchForm()
    if request.method == "POST":
        session = db_session.create_session()
        query = session.query(Student)
        if form.name_student.data:
            query = query.filter(Student.name_student.ilike(f"%{form.name_student.data}%"))
        if form.name_parent.data:
            query = query.filter(Student.name_parent.ilike(f"%{form.name_parent.data}%"))
        if form.birthday.data:
            birthday = datetime.strptime(form.birthday.data, "%d.%m.%Y").date()
            query = query.filter(Student.birthday == birthday)
        if form.document.data:
            query = query.filter(Student.document.ilike(f"%{form.document.data}%"))
        if form.region.data:
            city_title = next(
                (city["title"] for city in get_cities_data(int(form.region.data)) if str(city["id"]) == form.city.data),
                "",
            )
            query = query.filter(Student.city == city_title)
        if form.school.data:
            school_title = next(
                (
                    school["title"]
                    for school in get_schools_data(int(form.city.data))
                    if str(school["id"]) == form.school.data
                ),
                "",
            )
            query = query.filter(Student.school == school_title)
        if form.PFDO.data:
            query = query.filter(Student.PFDO == form.PFDO.data)
        if form.parent_phone.data:
            query = query.filter(Student.parent_phone.ilike(f"%{form.parent_phone.data}%"))
        if form.student_phone.data:
            query = query.filter(Student.student_phone.ilike(f"%{form.student_phone.data}%"))
        if form.school_class.data:
            query = query.filter(Student.school_class == form.school_class.data)
        if form.adres_of_living.data:
            query = query.filter(Student.adres_of_living.ilike(f"%{form.adres_of_living.data}%"))
        students = query.all()
        return render_template("students.html", students=students)
    return render_template("search.html", form=form)
