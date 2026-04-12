from app import app
from flask import render_template, request
from forms.add_schedule import AddScheduleForm
from data.db_session import create_session
from data.group import Group
from data.schedule import Schedule
from data.teacher import Teacher
from datetime import timedelta, datetime
from sqlalchemy.orm import joinedload
from babel.dates import format_date


def get_week_range(d1, d2):
    locale = "ru"
    year = d1.year

    if d1.month == d2.month:
        days = f"{d1.day}–{d2.day}"
        month_year = format_date(d2, format="MMMM yyyy г.", locale=locale)
        return f"{days} {month_year}"
    else:
        start = format_date(d1, format="d MMMM", locale=locale)
        end = format_date(d2, format="d MMMM yyyy г.", locale=locale)
        return f"{start} — {end}"


def get_full_teachers_initials_by_column(teacher: Teacher):
    return f"{teacher.name} {teacher.patronymic} {teacher.surename}"


@app.route("/add_schedule", methods=["GET", "POST"])
def add_schedule():
    form = AddScheduleForm()
    db_sess = create_session()
    form.group.choices = [
        (group.id, f'"{group.name_of_group}" c {get_full_teachers_initials_by_column(group.teacher)}')
        for group in db_sess.query(Group).all()
    ]
    if form.validate_on_submit():
        is_there_problem = False
        schedule = Schedule()
        schedule.group_id = int(form.group.data)
        schedule.date = form.datetime.data.date()
        dt = form.datetime.data
        duration = timedelta(hours=form.duration.data.hour, minutes=form.duration.data.minute)
        end_dt = duration + dt
        schedule.start_time = dt.time()
        schedule.end_time = end_dt.time()
        print(dt.hour * 60 + dt.minute + duration.seconds / 60)
        # проверка, что занятие кончиться в тот же день когда и началось
        if dt.hour * 60 + dt.minute + duration.seconds / 60 >= 24 * 60:
            form.duration.errors.append("the lesson may not start and end on different days")
            is_there_problem = True
        if not is_there_problem:
            db_sess.add(schedule)
            db_sess.commit()
    return render_template("add_schedule.html", form=form)


@app.route("/show_schedules")
def show_schedules():
    return render_template("show_schedules.html")


@app.route("/get_more_days")
def get_more_days():
    start_date_str = request.args.get("start_date")
    first_day_of_week = datetime.strptime(start_date_str, "%Y-%m-%d")
    first_day_of_week -= timedelta(days=first_day_of_week.weekday())
    last_day_of_week = first_day_of_week + timedelta(days=7)
    db_sess = create_session()
    schedules = db_sess.query(Schedule).options(joinedload(Schedule.group)).all()

    unique_times = sorted(
        list(set(f'{s.start_time.strftime("%H:%M")}-{s.end_time.strftime("%H:%M")}' for s in schedules))
    )

    matrix = []
    for time_key in unique_times:
        row = [time_key]  # Первая колонка — время
        for day_offset in range(7):
            cur_date = first_day_of_week + timedelta(days=day_offset)
            events = []
            for s in schedules:
                s_time = f'{s.start_time.strftime("%H:%M")}-{s.end_time.strftime("%H:%M")}'
                if s_time == time_key and s.is_schedule_at_date(cur_date):
                    events.append({"title": s.group.name_of_group})
            row.append(events)
        matrix.append(row)

    next_date = (first_day_of_week + timedelta(days=7)).strftime("%Y-%m-%d")
    print(matrix)
    return render_template(
        "show_schedules_batch.html",
        matrix=matrix,
        next_date=next_date,
        week_interval=get_week_range(first_day_of_week, last_day_of_week),
    )
