from flask import render_template, flash, redirect, url_for, request
from data import db_session
from data.level_contest import Level_contest
from data.qualification_course import QualificationCourse
from data.teacher_qualification import TeacherQualification
from data.teacher import Teacher
from datetime import date, datetime
from app import app


@app.route("/qualification_courses")
def qualification_courses():
    db_sess = db_session.create_session()
    courses = db_sess.query(QualificationCourse).all()
    today = date.today()
    return render_template("qualification_courses.html",
                           courses=courses,
                           today=today,
                           date=date)


@app.route("/qualification_courses/<int:course_id>")
def qualification_course_details(course_id):
    db_sess = db_session.create_session()
    course = db_sess.query(QualificationCourse).get(course_id)
    if not course:
        flash("Курс не найден", "danger")
        return redirect(url_for('qualification_courses'))
    return render_template("qualification_course_details.html", course=course, date=date)


@app.route('/add_qualification_course', methods=['GET', 'POST'])
def add_qualification_course():
    db_sess = db_session.create_session()
    levels = db_sess.query(Level_contest).all()

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
        course.level_id = int(request.form.get("level_id"))

        db_sess.add(course)
        db_sess.commit()
        flash('Курс успешно добавлен!', 'success')
        return redirect(url_for('qualification_courses'))

    return render_template('add_edit_qualification_courses.html',
                           title='Добавить курс повышения квалификации',
                           levels=levels,
                           course=None)


@app.route('/edit_qualification_course/<int:course_id>', methods=['GET', 'POST'])
def edit_qualification_course(course_id):
    db_sess = db_session.create_session()
    course = db_sess.query(QualificationCourse).get(course_id)
    if not course:
        flash('Курс не найден', 'danger')
        return redirect(url_for('qualification_courses'))
    levels = db_sess.query(Level_contest).all()
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
        course.link = request.form.get('link')
        course.description = request.form.get('description')
        course.level_id = int(request.form.get("level_id"))

        db_sess.commit()
        flash('Курс успешно обновлен!', 'success')
        return redirect(url_for('qualification_course_details', course_id=course.id))

    return render_template('add_edit_qualification_courses.html',
                           title='Редактировать курс',
                           levels=levels,
                           course=course)