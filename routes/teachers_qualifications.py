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
    courses = db_sess.query(QualificationCourse).all()
    today = date.today()
    return render_template("teachers_qualifications.html",
                           courses=courses,
                           today=today,
                           date=date)


@app.route("/teachers_qualifications/<int:course_id>")
def teachers_qualification_details(course_id):
    db_sess = db_session.create_session()
    course = db_sess.query(QualificationCourse).get(course_id)
    if not course:
        flash("Курс не найден", "danger")
        return redirect(url_for('teachers_qualifications'))
    return render_template("teachers_qualification_details.html", course=course, date=date)


@app.route('/add_teacher_qualification', methods=['GET', 'POST'])
def add_teacher_qualification():
    db_sess = db_session.create_session()

    if request.method == 'POST':
        course = QualificationCourse()
        course.program_name = request.form.get('program_name')

        start_date = request.form.get('start_date')
        if start_date:
            try:
                course.start_date = datetime.strptime(start_date, '%d.%m.%Y').date()
            except ValueError:
                course.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        end_date = request.form.get('end_date')
        if end_date:
            try:
                course.end_date = datetime.strptime(end_date, '%d.%m.%Y').date()
            except ValueError:
                course.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        course.hours = int(request.form.get('hours')) if request.form.get('hours') else None
        course.organization = request.form.get('organization')
        course.link = request.form.get('link')
        course.place = request.form.get('place')

        db_sess.add(course)
        db_sess.commit()
        flash('Курс успешно добавлен!', 'success')
        return redirect(url_for('teachers_qualifications'))

    return render_template('add_edit_teacher_qualification.html',
                           title='Добавить курс повышения квалификации',
                           course=None)


@app.route('/edit_teacher_qualification/<int:course_id>', methods=['GET', 'POST'])
def edit_teacher_qualification(course_id):
    db_sess = db_session.create_session()
    course = db_sess.query(QualificationCourse).get(course_id)
    if not course:
        flash('Курс не найден', 'danger')
        return redirect(url_for('teachers_qualifications'))

    if request.method == 'POST':
        course.program_name = request.form.get('program_name')

        start_date = request.form.get('start_date')
        if start_date:
            try:
                course.start_date = datetime.strptime(start_date, '%d.%m.%Y').date()
            except ValueError:
                try:
                    course.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    course.start_date = None
        else:
            course.start_date = None

        end_date = request.form.get('end_date')
        if end_date:
            try:
                course.end_date = datetime.strptime(end_date, '%d.%m.%Y').date()
            except ValueError:
                try:
                    course.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    course.end_date = None
        else:
            course.end_date = None

        course.hours = int(request.form.get('hours')) if request.form.get('hours') else None
        course.organization = request.form.get('organization')
        course.place = request.form.get('place')
        course.level = request.form.get('level')
        course.link = request.form.get('link')
        course.description = request.form.get('description')

        db_sess.commit()
        flash('Курс успешно обновлен!', 'success')
        return redirect(url_for('teachers_qualification_details', course_id=course.id))

    return render_template('add_edit_teacher_qualification.html',
                           title='Редактировать курс',
                           course=course)