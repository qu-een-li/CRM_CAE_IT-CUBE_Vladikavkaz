from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from data import db_session
from data.contest import Contest
from data.direction import Direction
from data.level_contest import Level_contest
from datetime import date
from app import app


@app.route("/contests")
def contests_list():
    db_sess = db_session.create_session()
    contests = db_sess.query(Contest).all()
    today = date.today()
    return render_template("contests.html", contests=contests, today=today)


@app.route("/contest/<int:contest_id>")
def contest_details(contest_id):
    db_sess = db_session.create_session()
    contest = db_sess.query(Contest).get(contest_id)
    if not contest:
        flash("Конкурс не найден", "danger")
        return redirect(url_for("contests_list"))
    return render_template("contest_details.html", contest=contest)


@app.route('/add_contest', methods=['GET', 'POST'])
@login_required
def add_contest():
    db_sess = db_session.create_session()
    directions = db_sess.query(Direction).all()
    levels = db_sess.query(Level_contest).all()

    if request.method == 'POST':
        contest = Contest()
        contest.name = request.form.get('name')
        contest.date = request.form.get('start_date')
        contest.end_date = request.form.get('end_date') if request.form.get('end_date') else None
        contest.direction_id = int(request.form.get('direction_id'))
        contest.link_contest = request.form.get('link_contest')
        contest.description = request.form.get('description')
        contest.level_id = int(request.form.get('level_id'))
        contest.contest_organizer = request.form.get('contest_organizer')

        db_sess.add(contest)
        db_sess.commit()
        flash('Конкурс успешно добавлен!', 'success')
        return redirect(url_for('contests_list'))

    return render_template('add_edit_contest.html',
                           directions=directions,
                           levels=levels,
                           title='Добавить конкурс',
                           contest=None)


@app.route('/edit_contest/<int:contest_id>', methods=['GET', 'POST'])
@login_required
def edit_contest(contest_id):
    if current_user.role != 'admin':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('index'))

    db_sess = db_session.create_session()
    contest = db_sess.query(Contest).get(contest_id)
    if not contest:
        flash('Конкурс не найден', 'danger')
        return redirect(url_for('contests_list'))

    directions = db_sess.query(Direction).all()
    levels = db_sess.query(Level_contest).all()

    if request.method == 'POST':
        contest.name = request.form.get('name')
        contest.date = request.form.get('start_date')
        contest.end_date = request.form.get('end_date') if request.form.get('end_date') else None
        contest.direction_id = int(request.form.get('direction_id'))
        contest.link_contest = request.form.get('link_contest')
        contest.description = request.form.get('description')
        contest.level_id = int(request.form.get('level_id'))
        contest.contest_organizer = request.form.get('contest_organizer')

        db_sess.commit()
        flash('Конкурс успешно обновлен!', 'success')
        return redirect(url_for('contest_details', contest_id=contest.id))

    return render_template('add_edit_contest.html',
                           directions=directions,
                           levels=levels,
                           title='Редактировать конкурс',
                           contest=contest)

