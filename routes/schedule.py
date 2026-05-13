from app import app
from flask import render_template, request
from forms.add_schedule import AddScheduleForm
from data.group import Group
from data.schedule import Schedule
from data.teacher import Teacher
from datetime import timedelta, datetime
from babel.dates import format_date
from api.api_base import api_request


def get_week_range(d1, d2):
    """Получить отформатированный период между двумя датами
    в виде строки для заголовка в неделе расписания"""
    locale = "ru"

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
    """Добавить событие (на данный момент только еженедельное)"""
    form = AddScheduleForm()
    form.group.choices = [
        (
            group.id,
            f'"{group.name_of_group}" c {get_full_teachers_initials_by_column(Teacher.from_dict(api_request(f'v1/teachers/{group.teacher_id}')))}',
        )
        for group in map(Group.from_dict, api_request("/v1/groups/"))
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

        # проверка, что занятие кончиться в тот же день когда и началось
        if dt.hour * 60 + dt.minute + duration.seconds / 60 >= 24 * 60:
            form.duration.errors.append("the lesson may not start and end on different days")
            is_there_problem = True
        if not is_there_problem:
            print(api_request("v1/schedules/", method="POST", data=schedule.to_dict()))
    return render_template("add_schedule.html", form=form)


@app.route("/show_schedules")
def show_schedules():
    """Страница расписания"""
    group_id = request.args.get("group_id")
    id_and_group_names = api_request("v1/groups", data={"fields": ["id", "name_of_group"]})
    return render_template("show_schedules.html", id_and_group_names=id_and_group_names, group_id_filter=group_id)


@app.route("/get_more_days")
def get_more_days():
    """Загрузка расписания по неделям в страницу расписания"""
    group_id = request.args.get("group_id")
    n_of_weeks = 3
    start_date_str = request.args.get("start_date")

    current_week_start = datetime.strptime(start_date_str, "%Y-%m-%d")
    current_week_start -= timedelta(days=current_week_start.weekday())

    list_of_matrix_and_interval = []
    days_lists = []

    schedules = [Schedule.from_dict(d) for d in api_request("/v1/schedules/")]
    if group_id:
        schedules = [s for s in schedules if s.group_id == int(group_id)]

    unique_times = sorted(
        list(set(f'{s.start_time.strftime("%H:%M")}-{s.end_time.strftime("%H:%M")}' for s in schedules))
    )

    for _ in range(n_of_weeks):
        week_days_iso = [(current_week_start + timedelta(days=(d))).date().isoformat() for d in range(7)]
        days_lists.append(week_days_iso)

        matrix = []
        for time_key in unique_times:
            row = [time_key]
            for day_offset in range(7):
                cur_date = current_week_start + timedelta(days=day_offset)
                events = []
                for s in schedules:
                    s_time = f'{s.start_time.strftime("%H:%M")}-{s.end_time.strftime("%H:%M")}'
                    if s_time == time_key and s.is_schedule_at_date(cur_date):
                        group_info = api_request(f"/v1/groups/{s.group_id}", params={"fields": ["name_of_group", "id"]})
                        events.append({"title": group_info["name_of_group"], "id": s.id})
                row.append(events)
            matrix.append(row)

        week_end = current_week_start + timedelta(days=6)
        list_of_matrix_and_interval.append((matrix, get_week_range(current_week_start, week_end)))

        current_week_start += timedelta(days=7)

    next_date_str = current_week_start.strftime("%Y-%m-%d")

    return render_template(
        "show_schedules_batch.html",
        list_of_matrix=list_of_matrix_and_interval,
        next_date=next_date_str,
        days_lists=days_lists,
    )
