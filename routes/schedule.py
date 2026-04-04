from app import app
from flask import render_template, request
from forms.add_schedule import AddScheduleForm
from data import db_session
from data.group import Group
from data.schedule import Schedule
from data.teacher import Teacher
from datetime import timedelta


def get_full_teachers_initials_by_column(teacher: Teacher):
    return f'{teacher.name} {teacher.patronymic} {teacher.surename}'


@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    form = AddScheduleForm()
    db_sess = db_session.create_session()
    form.group.choices = [(group.id, f'"{group.name_of_group}" c {get_full_teachers_initials_by_column(group.teacher)}')
                          for group in db_sess.query(Group).all()]
    if form.validate_on_submit():
        is_there_problem = False
        schedule = Schedule()
        schedule.group_id = int(form.group.data)
        schedule.date = form.datetime.data.date()
        dt = form.datetime.data
        duration = timedelta(hours=form.duration.data.hour,
                             minutes=form.duration.data.minute)
        end_dt = duration + dt
        schedule.start_time = dt.time()
        schedule.end_time = end_dt.time()
        print(dt.hour * 60 + dt.minute + duration.seconds / 60)
        # проверка, что занятие кончиться в тот же день когда и началось
        if dt.hour * 60 + dt.minute + duration.seconds / 60 >= 24 * 60:
            form.duration.errors.append(
                "the lesson may not start and end on different days")
            is_there_problem = True
        if not is_there_problem:
            db_sess.add(schedule)
            db_sess.commit()
    return render_template('add_schedule.html', form=form)
