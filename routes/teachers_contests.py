from flask import render_template
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