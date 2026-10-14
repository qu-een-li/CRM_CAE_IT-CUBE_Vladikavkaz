# routes/teachers.py
from app import app
from flask import render_template, request, redirect, jsonify, flash, send_from_directory, url_for
from data import db_session
from data.teacher_in_contests import Teacher_in_Contests
from data.teacher import Teacher
from data.student_in_contest import Student_in_Contest
from data.contest_for_teachers import Contest_for_Teachers
from data.teacher_qualification import TeacherQualification
from data.qualification_course import QualificationCourse
from data.user import User, UserRole
from forms.teacher_form import TeacherForm
import os
from datetime import datetime, date
from config import UPLOAD_FOLDER
from werkzeug.utils import secure_filename
from re import match

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def delete_old_photo(filename):
    """Функция для удаления старого фото при изменении даннных"""
    if filename and filename != "anonymous.jpg":
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Удалено старое фото: {file_path}")


@app.route("/add_teacher", methods=["GET", "POST"])
def add_teacher():
    form = TeacherForm()

    if form.validate_on_submit():
        try:
            session = db_session.create_session()

            if session.query(Teacher).filter(Teacher.email == form.email.data).first():
                return render_template("add_teacher.html", form=form, message="Наставник с таким email уже существует")

            photo_filename = "anonymous.jpg"
            if form.photo.data:
                photo = form.photo.data
                if photo and allowed_file(photo.filename):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_ext = photo.filename.rsplit(".", 1)[1].lower()
                    photo_filename = secure_filename(f"{timestamp}_{form.surename.data}_{form.name.data}_{file_ext}")
                    photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))

            teacher = Teacher(
                surename=form.surename.data,
                name=form.name.data,
                patronymic=form.patronymic.data,
                phone=form.phone.data,
                email=form.email.data,
                personal_photos=photo_filename,
                category=form.category.data,
                rate=float(form.rate.data),
                work_condition=form.work_condition.data
            )
            teacher.birthday = datetime.strptime(form.birthday.data, "%d.%m.%Y").date()
            teacher.experience_start = datetime.strptime(form.experience_start.data, "%d.%m.%Y").date()
            teacher.hire_date = datetime.strptime(form.hire_date.data, "%d.%m.%Y").date()

            if form.graduation_date.data:
                teacher.graduation_date = datetime.strptime(form.graduation_date.data, "%d.%m.%Y").date()
            session.add(teacher)
            session.flush()

            if form.allow_login.data:
                if not form.user_name.data:
                    form.user_name.errors.append("Без этого поля человек не сможет входить в систему")
                if not form.password.data:
                    form.password.errors.append("Без этого поля человек не сможет входить в систему")
                else:
                    if len(form.password.data) <= 3:
                        form.password.errors.append("Пароль должен быть больше 3-ех символов")
                if form.user_name.errors or form.password.errors:
                    return render_template("add_teacher.html", form=form)
                user = User(user_name=form.user_name.data)
                user.set_password(form.password.data)
                user.id_in_column_of_role = teacher.id
                user.role = UserRole.TEACHER
                session.add(user)

            session.commit()
            flash("Наставник успешно добавлен", "success")
            return redirect("/teachers")

        except Exception as e:
            session.rollback()
            flash(f"Ошибка при сохранении: {str(e)}", "danger")
            return render_template("add_teacher.html", form=form)
        finally:
            session.close()

    return render_template("add_teacher.html", form=form)


@app.route("/teachers")
def list_of_teachers():
    """Страница списка учителей"""
    try:
        session = db_session.create_session()

        # по умолчанию 0 - только работающие
        show_all = request.args.get('show_all', '0')

        if show_all == '1':
            # Все педагоги
            teachers = session.query(Teacher).all()
        else:
            # Только работающие
            teachers = session.query(Teacher).filter(Teacher.dismissal_date.is_(None)).all()

        return render_template("teachers.html", teachers=teachers, show_all=show_all)
    finally:
        session.close()


@app.route("/edit_teacher/<int:teacher_id>", methods=["GET", "POST"])
def edit_teacher(teacher_id):
    try:
        db_sess = db_session.create_session()
        teacher = db_sess.query(Teacher).get(teacher_id)

        if not teacher:
            flash("Наставник не найден", "danger")
            return redirect("/teachers")

        form = TeacherForm(obj=teacher)
        if request.method == "GET":
            if teacher.birthday:
                form.birthday.data = teacher.birthday.strftime("%d.%m.%Y")
            if teacher.phone:
                phone_str = str(teacher.phone)
                if len(phone_str) == 11:
                    form.phone.data = f"+7 {phone_str[1:4]} {phone_str[4:7]}-{phone_str[7:9]}-{phone_str[9:11]}"
                else:
                    form.phone.data = phone_str
            if teacher.experience_start:
                form.experience_start.data = teacher.experience_start.strftime("%d.%m.%Y")
            if teacher.hire_date:
                form.hire_date.data = teacher.hire_date.strftime("%d.%m.%Y")
            if teacher.graduation_date:
                form.graduation_date.data = teacher.graduation_date.strftime("%d.%m.%Y")
            if teacher.dismissal_date:
                form.dismissal_date.data = teacher.dismissal_date.strftime("%d.%m.%Y")
            if teacher.category:
                form.category.data = teacher.category
            if teacher.rate:
                form.rate.data = teacher.rate
            if teacher.work_condition:
                form.work_condition.data = teacher.work_condition

        current_photo = teacher.personal_photos

        if form.validate_on_submit():
            old_photo = teacher.personal_photos
            new_photo_filename = old_photo

            if form.photo.data and form.photo.data.filename:
                photo = form.photo.data
                if photo and allowed_file(photo.filename):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_name = secure_filename(f"{form.surename.data}_{form.name.data}".replace(" ", "_"))
                    file_ext = photo.filename.rsplit(".", 1)[1].lower()
                    new_photo_filename = f"{timestamp}_{safe_name}.{file_ext}"
                    photo.save(os.path.join(UPLOAD_FOLDER, new_photo_filename))
                    delete_old_photo(old_photo)

            teacher.surename = form.surename.data
            teacher.name = form.name.data
            teacher.patronymic = form.patronymic.data
            teacher.phone = form.phone.data
            teacher.email = form.email.data
            teacher.personal_photos = new_photo_filename
            teacher.birthday = datetime.strptime(form.birthday.data, "%d.%m.%Y").date()

            teacher.category = form.category.data
            teacher.rate = float(form.rate.data)
            teacher.work_condition = form.work_condition.data

            if form.experience_start.data:
                teacher.experience_start = datetime.strptime(form.experience_start.data, "%d.%m.%Y").date()
            if form.hire_date.data:
                teacher.hire_date = datetime.strptime(form.hire_date.data, "%d.%m.%Y").date()
            if form.graduation_date.data:
                teacher.graduation_date = datetime.strptime(form.graduation_date.data, "%d.%m.%Y").date()
            if form.dismissal_date.data:
                teacher.dismissal_date = datetime.strptime(form.dismissal_date.data, "%d.%m.%Y").date()
            else:
                teacher.dismissal_date = None

            db_sess.commit()
            flash("Данные наставника обновлены", "success")
            return redirect(url_for('teacher_profile', teacher_id=teacher.id))

        return render_template("edit_teacher.html", form=form, teacher_id=teacher_id, current_photo=current_photo)
    finally:
        db_sess.close()


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Скачивание файла из /uploads"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/teachers/<int:teacher_id>")
def teacher_profile(teacher_id):
    try:
        session = db_session.create_session()
        teacher = session.query(Teacher).get(teacher_id)

        if not teacher:
            flash("Наставник не найден", "danger")
            return redirect("/teachers")

        qualifications = session.query(TeacherQualification).filter_by(teacher_id=teacher_id).all()
        teacher_contests = session.query(Teacher_in_Contests).filter_by(teacher_id=teacher_id).all()
        student_contests = session.query(Student_in_Contest).filter_by(teacher_id=teacher_id).all()

        sort_by = request.args.get('sort', 'date')  # по умолчанию date

        if sort_by == 'level':
            teacher_contests = sorted(teacher_contests, key=lambda
                x: x.name_contest.level.name if x.name_contest and x.name_contest.level else '')
        elif sort_by == 'result':
            teacher_contests = sorted(teacher_contests, key=lambda x: (x.place or 999, x.rank or ''))
        else:
            teacher_contests = sorted(teacher_contests,
                                      key=lambda x: x.name_contest.date if x.name_contest else date.min, reverse=True)

        return render_template(
            "teacher_profile.html",
            teacher=teacher,
            qualifications=qualifications,
            teacher_contests=teacher_contests,
            student_contests=student_contests,
            date=date,
            sort_by=sort_by,
        )
    finally:
        session.close()
