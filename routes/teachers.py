# routes/teachers.py
from app import app
from flask import render_template, request, redirect, jsonify, flash, send_from_directory
from data import db_session
from data.teacher import Teacher
from forms.teacher_form import TeacherForm
import os
from datetime import datetime
from config import UPLOAD_FOLDER
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def delete_old_photo(filename):
    if filename and filename != "anonymous.jpg":
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Удалено старое фото: {file_path}")


@app.route("/add_teacher", methods=["GET", "POST"])
def add_teacher():
    form = TeacherForm()

    if form.validate_on_submit():
        session = db_session.create_session()

        if session.query(Teacher).filter(Teacher.email == form.email.data).first():
            return render_template("add_teacher.html", form=form, message="Наставник с таким email уже существует")

        photo_filename = "anonymous.jpg"
        if form.photo.data:
            photo = form.photo.data
            if photo and allowed_file(photo.filename):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = photo.filename.rsplit('.', 1)[1].lower()
                photo_filename = secure_filename(
                    f"{timestamp}_{form.surename.data}_{form.name.data}_{file_ext}")
                photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))

        teacher = Teacher(
            surename=form.surename.data,
            name=form.name.data,
            patronymic=form.patronymic.data,
            phone=form.phone.data,
            email=form.email.data,
            status=form.status.data,
            personal_photos=photo_filename
        )
        teacher.birthday = datetime.strptime(
            form.birthday.data, "%d.%m.%Y").date()

        session.add(teacher)
        session.commit()

        flash("Наставник успешно добавлен", "success")
        return redirect("/add_teacher")

    return render_template("add_teacher.html", form=form)


@app.route("/teachers")
def list_of_teachers():
    session = db_session.create_session()
    teachers = session.query(Teacher).all()
    return render_template("teachers.html", teachers=teachers)


@app.route("/edit_teacher/<int:teacher_id>", methods=["GET", "POST"])
def edit_teacher(teacher_id):
    db_sess = db_session.create_session()
    teacher = db_sess.query(Teacher).get(teacher_id)

    if not teacher:
        flash("Наставник не найден", "danger")
        return redirect("/teachers")

    form = TeacherForm(obj=teacher)

    current_photo = teacher.personal_photos

    if form.validate_on_submit():
        old_photo = teacher.personal_photos
        new_photo_filename = old_photo

        if form.photo.data and form.photo.data.filename:
            photo = form.photo.data
            if photo and allowed_file(photo.filename):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = secure_filename(f"{form.surename.data}_{form.name.data}".replace(' ', '_'))
                file_ext = photo.filename.rsplit('.', 1)[1].lower()
                new_photo_filename = f"{timestamp}_{safe_name}.{file_ext}"
                photo.save(os.path.join(UPLOAD_FOLDER, new_photo_filename))
                delete_old_photo(old_photo)

        phone_digits = ''.join(filter(str.isdigit, form.phone.data))

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


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
