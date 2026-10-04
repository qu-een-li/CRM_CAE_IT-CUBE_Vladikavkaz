from flask import render_template, flash, redirect, url_for, request
from data import db_session
from data.teacher_qualification import TeacherQualification
from data.teacher import Teacher
from data.qualification_course import QualificationCourse
from datetime import datetime
from app import app


@app.route("/add_teacher_qualification", methods=["GET", "POST"])
def add_teacher_qualification():
    db_sess = db_session.create_session()
    teachers = db_sess.query(Teacher).all()
    courses = db_sess.query(QualificationCourse).all()
    preselected_teacher_id = request.args.get("teacher_id", type=int)

    teacher_course_ids_map = {
        t.id: {q.course_id for q in db_sess.query(TeacherQualification).filter_by(teacher_id=t.id).all()}
        for t in teachers
    }

    if request.method == 'POST':
        qualification = TeacherQualification()

        teacher_id = request.form.get('teacher_id')
        if teacher_id:
            qualification.teacher_id = int(teacher_id)

        course_id = request.form.get('course_id')
        if course_id:
            qualification.course_id = int(course_id)
        else:
            flash('Выберите курс из списка', 'danger')
            return render_template('add_teacher_qualification.html',
                                   teachers=teachers,
                                   courses=courses,
                                   teacher_course_ids_map=teacher_course_ids_map,
                                   title='Добавить запись о повышении квалификации',
                                   preselected_teacher_id=preselected_teacher_id)

        existing = db_sess.query(TeacherQualification).filter_by(
            teacher_id=qualification.teacher_id,
            course_id=qualification.course_id
        ).first()
        if existing:
            flash('Этот курс уже добавлен преподавателю', 'warning')
            return redirect(url_for('teacher_profile', teacher_id=qualification.teacher_id))

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
                           teacher_course_ids_map=teacher_course_ids_map,
                           title='Добавить запись о повышении квалификации',
                           preselected_teacher_id=preselected_teacher_id)


@app.route("/delete_teacher_qualification/<int:qualification_id>", methods=["POST"])
def delete_teacher_qualification(qualification_id):
    db_sess = db_session.create_session()
    qualification = db_sess.query(TeacherQualification).get(qualification_id)

    if not qualification:
        flash("Запись не найдена", "danger")
        return redirect(url_for("qualification_courses"))

    teacher_id = qualification.teacher_id

    try:
        db_sess.delete(qualification)
        db_sess.commit()
        flash("Запись о повышении квалификации успешно удалена", "success")
    except Exception as e:
        db_sess.rollback()
        flash(f"Ошибка при удалении: {str(e)}", "danger")

    return redirect(url_for("teacher_profile", teacher_id=teacher_id))


@app.route("/edit_teacher_qualification/<int:qualification_id>", methods=["GET", "POST"])
def edit_teacher_qualification(qualification_id):
    db_sess = db_session.create_session()
    qualification = db_sess.query(TeacherQualification).get(qualification_id)

    if not qualification:
        flash("Запись не найдена", "danger")
        return redirect(url_for('qualification_courses'))

    teachers = db_sess.query(Teacher).all()
    courses = db_sess.query(QualificationCourse).all()

    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        if teacher_id:
            qualification.teacher_id = int(teacher_id)

        course_id = request.form.get('course_id')
        if course_id:
            qualification.course_id = int(course_id)
        else:
            flash('Выберите курс из списка', 'danger')
            return render_template('edit_teacher_qualification.html',
                                   qualification=qualification,
                                   teachers=teachers,
                                   courses=courses)

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

        db_sess.commit()
        flash('Запись успешно обновлена!', 'success')
        return redirect(url_for('teacher_profile', teacher_id=qualification.teacher_id))

    return render_template('edit_teacher_qualification.html',
                           qualification=qualification,
                           teachers=teachers,
                           courses=courses)