from flask import render_template, flash, redirect, url_for, request
from data import db_session
from data.qualification_course import QualificationCourse
from data.teacher_qualification import TeacherQualification
from data.teacher import Teacher
from datetime import date, datetime
from app import app


@app.route("/teachers_qualifications")
def teachers_qualifications():
    db_sess = db_session.create_session()
    qualifications = db_sess.query(TeacherQualification).all()
    teachers = db_sess.query(Teacher).all()
    courses = db_sess.query(QualificationCourse).all()
    today = date.today()
    return render_template("teachers_qualifications.html",
                         qualifications=qualifications,
                         teachers=teachers,
                         courses=courses,
                         today=today,
                         date=date)