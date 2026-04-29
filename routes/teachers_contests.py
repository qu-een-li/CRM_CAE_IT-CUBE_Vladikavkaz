from flask import render_template, flash, redirect, url_for
from data import db_session
from data.contest_for_teachers import Contest_for_Teachers
from datetime import date
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
        return redirect(url_for("contests_list"))
    return render_template("teachers_contest_details.html", contest=contest)