from flask import render_template, flash, redirect, url_for, request
from data import db_session
from data.teacher_in_contests import Teacher_in_Contests
from data.contest_for_teachers import Contest_for_Teachers
from data.teacher import Teacher
from app import app


@app.route("/add_teacher_in_contest", methods=["GET", "POST"])
def add_teacher_in_contest():
    db_sess = db_session.create_session()
    teachers = db_sess.query(Teacher).all()
    contests = db_sess.query(Contest_for_Teachers).all()
    preselected_teacher_id = request.args.get("teacher_id", type=int)

    if request.method == 'POST':
        teacher_contest = Teacher_in_Contests()

        teacher_contest.teacher_id = int(request.form.get('teacher_id'))
        teacher_contest.contest_id = int(request.form.get('contest_id'))

        place = request.form.get('place')
        if place:
            teacher_contest.place = int(place)

        teacher_contest.rank = request.form.get('rank')

        db_sess.add(teacher_contest)
        db_sess.commit()

        flash('Участие в конкурсе успешно добавлено!', 'success')
        return redirect(url_for('teacher_profile', teacher_id=teacher_contest.teacher_id))

    return render_template('add_teacher_in_contest.html',
                           teachers=teachers,
                           contests=contests,
                           title='Добавить участие в конкурсе',
                           preselected_teacher_id=preselected_teacher_id)


@app.route("/edit_teacher_in_contest/<int:contest_link_id>", methods=["GET", "POST"])
def edit_teacher_in_contest(contest_link_id):
    db_sess = db_session.create_session()
    teacher_contest = db_sess.query(Teacher_in_Contests).get(contest_link_id)

    if not teacher_contest:
        flash("Запись не найдена", "danger")
        return redirect(url_for("teachers_list"))

    teachers = db_sess.query(Teacher).all()
    contests = db_sess.query(Contest_for_Teachers).all()

    if request.method == 'POST':
        teacher_contest.teacher_id = int(request.form.get('teacher_id'))
        teacher_contest.contest_id = int(request.form.get('contest_id'))

        place = request.form.get('place')
        if place:
            teacher_contest.place = int(place)
        else:
            teacher_contest.place = None

        teacher_contest.rank = request.form.get('rank')

        db_sess.commit()
        flash('Участие в конкурсе обновлено!', 'success')
        return redirect(url_for('teacher_profile', teacher_id=teacher_contest.teacher_id))

    return render_template('add_teacher_contest.html',
                           teachers=teachers,
                           contests=contests,
                           title='Редактировать участие в конкурсе',
                           teacher_contest=teacher_contest,
                           preselected_teacher_id=teacher_contest.teacher_id)


@app.route("/delete_teacher_in_contest/<int:contest_link_id>", methods=["POST"])
def delete_teacher_in_contest(contest_link_id):
    db_sess = db_session.create_session()
    teacher_contest = db_sess.query(Teacher_in_Contests).get(contest_link_id)

    if not teacher_contest:
        flash("Запись не найдена", "danger")
        return redirect(url_for("teachers_list"))

    teacher_id = teacher_contest.teacher_id

    db_sess.delete(teacher_contest)
    db_sess.commit()
    flash("Участие в конкурсе удалено", "success")

    return redirect(url_for("teacher_profile", teacher_id=teacher_id))