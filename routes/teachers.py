# routes/teachers.py
from app import app
from flask import render_template, request, redirect, jsonify, flash, send_from_directory
from data import db_session
from data.teacher_in_contests import Teacher_in_Contests
from data.teacher import Teacher
from data.contest_for_teachers import Contest_for_Teachers
from data.teacher_qualification import TeacherQualification
from data.qualification_course import QualificationCourse
from forms.teacher_form import TeacherForm
import os
from datetime import datetime, date
from config import UPLOAD_FOLDER
from werkzeug.utils import secure_filename

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
    """Форма добавления учителя"""
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
                status=form.status.data,
                personal_photos=photo_filename,
            )
            teacher.birthday = datetime.strptime(form.birthday.data, "%d.%m.%Y").date()

            session.add(teacher)
            session.commit()

            flash("Наставник успешно добавлен", "success")
            return redirect("/add_teacher")
        finally:
            session.close()
    return render_template("add_teacher.html", form=form)


@app.route("/teachers")
def list_of_teachers():
    """Страница списка учителей"""
    try:
        session = db_session.create_session()
        teachers = session.query(Teacher).all()
        return render_template("teachers.html", teachers=teachers)
    finally:
        session.close()


@app.route("/edit_teacher/<int:teacher_id>", methods=["GET", "POST"])
def edit_teacher(teacher_id):
    """Форма изменения данных об учителе"""
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
                form.phone.data = str(teacher.phone)
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

            phone_digits = "".join(filter(str.isdigit, form.phone.data))

            teacher.surename = form.surename.data
            teacher.name = form.name.data
            teacher.patronymic = form.patronymic.data
            teacher.phone = int(phone_digits) if phone_digits else 0
            teacher.email = form.email.data
            teacher.status = form.status.data
            teacher.personal_photos = new_photo_filename
            teacher.birthday = datetime.strptime(form.birthday.data, "%d.%m.%Y").date()

            db_sess.commit()
            return redirect("/teachers")

        return render_template("edit_teacher.html", form=form, teacher_id=teacher_id, current_photo=current_photo)
    finally:
        db_sess.close()


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Скачивание файла из /uploads"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/teachers/<int:teacher_id>")
def teacher_profile(teacher_id):
    """Страница профиля учителя"""
    try:
        session = db_session.create_session()
        teacher = session.query(Teacher).get(teacher_id)

        if not teacher:
            flash("Наставник не найден", "danger")
            return redirect("/teachers")

        qualifications = session.query(TeacherQualification).filter_by(teacher_id=teacher_id).all()

        teacher_contests = session.query(Teacher_in_Contests).filter_by(teacher_id=teacher_id).all()

        return render_template("teacher_profile.html",
                               teacher=teacher,
                               qualifications=qualifications,
                               teacher_contests=teacher_contests,
                               date=date)
    finally:
        session.close()
