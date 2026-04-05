from app import app
from flask import render_template, request
from forms.add_schedule import AddScheduleForm
from data.db_session import create_session
from data.group import Group
from data.schedule import Schedule
from data.teacher import Teacher
from datetime import timedelta, datetime
from sqlalchemy.orm import joinedload


def get_full_teachers_initials_by_column(teacher: Teacher):
    return f'{teacher.name} {teacher.patronymic} {teacher.surename}'


@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    form = AddScheduleForm()
    db_sess = create_session()
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


@app.route('/show_schedules')
def show_schedules():
    return render_template('show_schedules.html')


@app.route('/get_more_days')
def get_more_days():
    start_date_str = request.args.get('start_date')
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

    days_to_show = 5  # Грузим по {days_to_show} дня за раз
    payload = []
    db_sess = create_session()
    schedules = db_sess.query(Schedule).options(
        joinedload(Schedule.group)).all()
    for i in range(days_to_show):
        current_day = start_date + timedelta(days=i)
        events = []
        for schedule in schedules:
            if schedule.is_schedule_at_date(current_day):
                group = schedule.group
                group: Group
                event = {"title": group.name_of_group, "description": group.description,
                         "teacher": get_full_teachers_initials_by_column(group.teacher)}
                events.append(event)
        payload.append({
            "date_string": current_day.strftime('%A, %d %B %Y').capitalize(),
            "events": events
        })

    next_date = (start_date + timedelta(days=days_to_show)
                 ).strftime('%Y-%m-%d')

    return render_template('show_schedules_batch.html', days=payload, next_date=next_date)
