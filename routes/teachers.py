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


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
