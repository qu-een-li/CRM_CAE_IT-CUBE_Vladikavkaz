from flask import render_template, flash, redirect, url_for, request
from data import db_session
from data.qualification_course import QualificationCourse
from data.teacher_qualification import TeacherQualification
from data.teacher import Teacher
from datetime import datetime
from app import app


@app.route("/add_teacher_qualification", methods=["GET", "POST"])
def add_teacher_qualification():
    db_sess = db_session.create_session()
    teachers = db_sess.query(Teacher).all()
    courses = db_sess.query(QualificationCourse).all()
    preselected_teacher_id = request.args.get("teacher_id", type=int)

    if request.method == 'POST':
        qualification = TeacherQualification()

        course_id = request.form.get('course_id')
        if course_id:
            qualification.course_id = int(course_id)
        else:
            flash('Выберите курс из списка', 'danger')
            return redirect(request.url)

        qualification.teacher_id = int(request.form.get('teacher_id'))
        qualification.registration_number = request.form.get('registration_number')
        qualification.certificate_number = request.form.get('certificate_number')

        issue_date = request.form.get('issue_date')
        if issue_date:
            try:
                qualification.issue_date = datetime.strptime(issue_date, '%d.%m.%Y').date()
            except ValueError:
                qualification.issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()

        qualification.issued_by = request.form.get('issued_by')
        qualification.link = request.form.get('link')

        db_sess.add(qualification)
        db_sess.commit()
        flash('Запись о повышении квалификации успешно добавлена!', 'success')

        return redirect(url_for('teacher_profile', teacher_id=qualification.teacher_id))

    return render_template('add_teacher_qualification.html',
                           teachers=teachers,
                           courses=courses,
                           title='Добавить запись о повышении квалификации',
                           preselected_teacher_id=preselected_teacher_id)


@app.route("/delete_teacher_qualification/<int:qualification_id>", methods=["POST"])
def delete_teacher_qualification(qualification_id):
    """Удаление записи о повышении квалификации"""
    db_sess = db_session.create_session()
    qualification = db_sess.query(TeacherQualification).get(qualification_id)

    if not qualification:
        flash("Запись не найдена", "danger")
        return redirect(url_for("teachers_qualifications_list"))

    teacher_id = qualification.teacher_id

    try:
        db_sess.delete(qualification)
        db_sess.commit()
        flash("Запись о повышении квалификации успешно удалена", "success")
    except Exception as e:
        db_sess.rollback()
        flash(f"Ошибка при удалении: {str(e)}", "danger")

    return redirect(url_for("teacher_profile", teacher_id=teacher_id))
