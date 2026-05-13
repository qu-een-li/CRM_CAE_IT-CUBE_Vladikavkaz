from app import app
from flask import render_template
from data.db_session import create_session
from data.teacher import Teacher
from data.group import Group


@app.route("/")
def index():
    """Главная страница"""
    ses = create_session()
    teachers = ses.query(Teacher).all()
    for teacher in teachers:
        if teacher.patronymic:
            teacher.fio = f"{teacher.surename} {teacher.name[0]}.{teacher.patronymic[0]}.".title()
        else:
            teacher.fio = f"{teacher.surename} {teacher.name[0]}.".title()
    groups = ses.query(Group).all()
    return render_template("index.html", teachers=teachers, groups=groups)
