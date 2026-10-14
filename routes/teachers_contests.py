from flask import render_template, flash, redirect, url_for, request
from data import db_session
from data.contest_for_teachers import Contest_for_Teachers
from data.level_contest import Level_contest
from datetime import date, datetime
from app import app


@app.route("/teachers_contests")
def teachers_contests_list():
    db_sess = db_session.create_session()
    contests = db_sess.query(Contest_for_Teachers).all()
    today = date.today()
    return render_template("teachers_contests.html", contests=contests, today=today, date=date)


@app.route("/teachers_contests/<int:contest_id>")
def teachers_contest_details(contest_id):
    db_sess = db_session.create_session()
    contest = db_sess.query(Contest_for_Teachers).get(contest_id)
    if not contest:
        flash("Конкурс не найден", "danger")
        return redirect(url_for("teachers_contests_list"))
    today = date.today()
    return render_template("teachers_contest_details.html", contest=contest, today=today, date=date)


@app.route("/add_teacher_contest", methods=["GET", "POST"])
def add_teacher_contest():
    db_sess = db_session.create_session()
    levels = db_sess.query(Level_contest).all()

    if request.method == "POST":
        contest = Contest_for_Teachers()
        contest.name = request.form.get("name")

        start_date = request.form.get("start_date")
        if start_date:
            try:
                contest.date = datetime.strptime(start_date, "%d.%m.%Y").date()
            except ValueError:
                contest.date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            flash('Дата начала обязательна', 'danger')
            return render_template("add_edit_teacher_contest.html", levels=levels, title="Добавить конкурс", contest=None)

        end_date = request.form.get("end_date")
        if end_date:
            try:
                contest.end_date = datetime.strptime(end_date, "%d.%m.%Y").date()
            except ValueError:
                contest.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        contest.link = request.form.get("link")
        contest.description = request.form.get("description")

        level_id = request.form.get("level_id")
        if level_id:
            contest.level_id = int(level_id)
        else:
            flash('Выберите уровень конкурса', 'danger')
            return render_template("add_edit_teacher_contest.html", levels=levels, title="Добавить конкурс", contest=None)

        contest.organizer = request.form.get("organizer")

        db_sess.add(contest)
        db_sess.commit()
        flash("Конкурс успешно добавлен!", "success")
        return redirect(url_for("teachers_contests_list"))

    return render_template("add_edit_teacher_contest.html", levels=levels, title="Добавить конкурс", contest=None)


@app.route("/edit_teacher_contest/<int:contest_id>", methods=["GET", "POST"])
def edit_teacher_contest(contest_id):
    db_sess = db_session.create_session()
    contest = db_sess.query(Contest_for_Teachers).get(contest_id)
    if not contest:
        flash("Конкурс не найден", "danger")
        return redirect(url_for("teachers_contests_list"))

    levels = db_sess.query(Level_contest).all()

    if request.method == "POST":
        contest.name = request.form.get("name")

        start_date = request.form.get("start_date")
        if start_date:
            try:
                contest.date = datetime.strptime(start_date, "%d.%m.%Y").date()
            except ValueError:
                contest.date = datetime.strptime(start_date, "%Y-%m-%d").date()

        end_date = request.form.get("end_date")
        if end_date:
            try:
                contest.end_date = datetime.strptime(end_date, "%d.%m.%Y").date()
            except ValueError:
                contest.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            contest.end_date = None

        contest.link = request.form.get("link")
        contest.description = request.form.get("description")

        level_id = request.form.get("level_id")
        if level_id:
            contest.level_id = int(level_id)
        else:
            flash('Выберите уровень конкурса', 'danger')
            return render_template("add_edit_teacher_contest.html", levels=levels, title="Редактировать конкурс", contest=contest)

        contest.organizer = request.form.get("organizer")

        db_sess.commit()
        flash("Конкурс успешно обновлен!", "success")
        return redirect(url_for("teachers_contest_details", contest_id=contest.id))

    return render_template(
        "add_edit_teacher_contest.html", levels=levels, title="Редактировать конкурс", contest=contest
    )


@app.route("/delete_teacher_contest/<int:contest_id>", methods=["POST"])
def delete_teacher_contest(contest_id):
    db_sess = db_session.create_session()
    contest = db_sess.query(Contest_for_Teachers).get(contest_id)
    if not contest:
        flash("Конкурс не найден", "danger")
        return redirect(url_for("teachers_contests_list"))

    try:
        db_sess.delete(contest)
        db_sess.commit()
        flash("Конкурс успешно удален!", "success")
    except Exception as e:
        db_sess.rollback()
        flash(f"Ошибка при удалении: {str(e)}", "danger")

    return redirect(url_for("teachers_contests_list"))