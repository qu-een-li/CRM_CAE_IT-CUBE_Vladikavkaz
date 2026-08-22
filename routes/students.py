from app import app
from flask import render_template, request, redirect, flash
from forms.registrationform import RegistrationForm
from data import db_session
from data.student import Student
from api.api_cities import get_cities_data
from api.api_schools import get_schools_data
from datetime import datetime


@app.route("/students", methods=["GET"])
def students():
    """Список студентов"""
    session = db_session.create_session()
    students = session.query(Student).all()
    return render_template("students.html", students=students)


# routes/students.py

@app.route("/add", methods=["POST", "GET"])
def add():
    form = RegistrationForm()
    session = db_session.create_session()

    try:
        if request.method == "POST":
            region_id = request.form.get("region")
            if region_id:
                try:
                    cities = get_cities_data(int(region_id))
                    form.city.choices = [(str(c['id']), c['title'])
                                         for c in cities]
                except ValueError:
                    pass  # Игнорируем ошибку, если id некорректен

            # Обновляем список школ, если выбран город
            city_id = request.form.get("city")
            if city_id:
                try:
                    schools = get_schools_data(int(city_id))
                    form.school.choices = [
                        (str(s['id']), s['title']) for s in schools]
                except ValueError:
                    pass

        if form.validate_on_submit():
            # Проверяем полноту данных для статуса кандидата
            optional_fields = [
                form.name_parent.data, form.birthday.data, form.document.data,
                form.parent_phone.data, form.student_phone.data,
                form.school_class.data, form.adres_of_living.data, form.school.data, form.city.data
            ]
            is_full_data = all(optional_fields)

            # Если данные неполные и нет подтверждения
            if not is_full_data and not form.confirm_candidate.data:
                flash(
                    "Заполнены не все поля. Ученик будет добавлен как КАНДИДАТ. Подтвердите действие галочкой ниже.", "warning")
                return render_template("registration.html", form=form, show_confirm=True)

            # Проверка на дубликат по ПФДО
            existing_student = session.query(Student).filter(
                Student.PFDO == form.PFDO.data).first()
            if existing_student:
                return render_template("registration.html", form=form, message="Ученик с таким номером ПФДО уже существует")

            # Получаем названия города и школы безопасно
            city_title = ""
            if form.region.data and form.city.data:
                try:
                    cities_list = get_cities_data(int(form.region.data))
                    city_obj = next((c for c in cities_list if str(
                        c["id"]) == form.city.data), None)
                    if city_obj:
                        city_title = city_obj["title"]
                except:
                    pass

            school_title = ""
            if form.city.data and form.school.data:
                try:
                    schools_list = get_schools_data(int(form.city.data))
                    school_obj = next((s for s in schools_list if str(
                        s["id"]) == form.school.data), None)
                    if school_obj:
                        school_title = school_obj["title"]
                except:
                    pass

            # Парсинг даты
            birthday_obj = None
            if form.birthday.data:
                try:
                    birthday_obj = datetime.strptime(
                        form.birthday.data, "%d.%m.%Y").date()
                except ValueError:
                    flash("Неверный формат даты рождения", "danger")
                    return render_template("registration.html", form=form)

            user = Student(
                name_student=form.name_student.data,
                name_parent=form.name_parent.data or "",
                birthday=birthday_obj,
                PFDO=form.PFDO.data,
                document=form.document.data or "",
                city=city_title,
                school=school_title,
                parent_phone=form.parent_phone.data or "",
                student_phone=form.student_phone.data or "",
                school_class=form.school_class.data,
                adres_of_living=form.adres_of_living.data or "",
                is_candidate=not is_full_data
            )

            session.add(user)
            session.commit()

            status = "Кандидат" if not is_full_data else "Ученик"
            flash(f"{status} успешно зарегистрирован!", "success")
            return redirect("/add")

        return render_template("registration.html", form=form)
    finally:
        session.close()


@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    """Форма изменения данных студента"""
    db_sess = db_session.create_session()
    try:
        student = db_sess.query(Student).get(student_id)
        if not student:
            return redirect("/students")

        # Инициализируем форму данными из базы
        form = RegistrationForm(obj=student)
        form.birthday.data = student.birthday.strftime("%d.%m.%Y")

        # Сохраняем текущие значения для отображения в JS (для выпадающих списков)
        curr_city = student.city
        curr_school = student.school

        # Логика обновления списков городов/школ при выборе региона (для AJAX-запросов внутри формы)
        if request.method == "POST":
            if "region" in request.form and request.form["region"]:
                try:
                    cities = get_cities_data(int(request.form["region"]))
                    form.city.choices = [(str(c['id']), c['title'])
                                         for c in cities]
                except ValueError:
                    pass

            if "city" in request.form and request.form["city"]:
                try:
                    schools = get_schools_data(int(request.form["city"]))
                    form.school.choices = [
                        (str(s['id']), s['title']) for s in schools]
                except ValueError:
                    pass

        if form.validate_on_submit():
            # 1. Проверяем полноту данных для снятия статуса кандидата
            optional_fields = [
                form.name_parent.data, form.birthday.data, form.document.data,
                form.parent_phone.data, form.student_phone.data,
                form.school_class.data, form.adres_of_living.data
            ]
            is_full_personal_data = all(optional_fields)
            has_location = bool(form.city.data and form.school.data)

            # 2. Обновляем данные вручную (Защита от удаления: если поле пустое, оставляем старое)

            # Обязательные поля обновляем всегда (или оставляем старые, если вдруг пришли пустыми)
            student.name_student = form.name_student.data or student.name_student
            student.PFDO = form.PFDO.data or student.PFDO

            # Опциональные поля обновляем только если в форме есть новое значение
            if form.name_parent.data:
                student.name_parent = form.name_parent.data
            if form.document.data:
                student.document = form.document.data
            if form.parent_phone.data:
                student.parent_phone = form.parent_phone.data
            if form.student_phone.data:
                student.student_phone = form.student_phone.data
            if form.school_class.data:
                student.school_class = form.school_class.data
            if form.adres_of_living.data:
                student.adres_of_living = form.adres_of_living.data

            # Обработка даты рождения
            if form.birthday.data:
                try:
                    student.birthday = datetime.strptime(
                        form.birthday.data, "%d.%m.%Y").date()
                except ValueError:
                    flash(
                        "Неверный формат даты рождения. Используйте ДД.ММ.ГГГГ", "danger")
                    # Возвращаем форму с ошибкой, не забывая передать student для шаблона
                    return render_template("edit_student.html", form=form, student_id=student_id,
                                           current_city=curr_city, current_school=curr_school, student=student)

            # Обработка Города и Школы (получаем текстовые названия по ID)
            city_title = student.city
            if form.region.data and form.city.data:
                try:
                    city_obj = next((c for c in get_cities_data(
                        int(form.region.data)) if str(c["id"]) == form.city.data), None)
                    if city_obj:
                        city_title = city_obj["title"]
                except:
                    pass

            school_title = student.school
            if form.city.data and form.school.data:
                try:
                    school_obj = next((s for s in get_schools_data(
                        int(form.city.data)) if str(s["id"]) == form.school.data), None)
                    if school_obj:
                        school_title = school_obj["title"]
                except:
                    pass

            student.city = city_title
            student.school = school_title

            # 3. Логика смены статуса Кандидата
            # Если заполнено ВСЁ (и личные данные, и локация), снимаем статус кандидата
            if is_full_personal_data and has_location:
                student.is_candidate = False

            db_sess.commit()
            flash("Данные ученика успешно обновлены", "success")
            return redirect("/students")

        # При GET-запросе или ошибке валидации рендерим шаблон
        # ВАЖНО: передаем student, чтобы в шаблоне работала проверка {% if student.is_candidate %}
        return render_template(
            "edit_student.html",
            form=form,
            student_id=student_id,
            current_city=curr_city,
            current_school=curr_school,
            student=student
        )
    finally:
        db_sess.close()
