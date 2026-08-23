from app import app
from flask import render_template, request, flash, redirect, url_for
from forms.add_schedule import AddScheduleForm
from data.group import Group
from data.schedule import Schedule
from data.teacher import Teacher
from babel.dates import format_date
from api.api_base import api_request
from data.db_session import create_session
from data.schedule import FrequencyType
from datetime import date
from sqlalchemy import select
from datetime import datetime, date, time, timedelta
import re


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


def parse_time_string(time_str):
    """Преобразует строку 'HH:MM' в объект time."""
    if not time_str:
        return None
    try:
        # Пробуем формат HH:MM
        match = re.match(r'^(\d{1,2}):(\d{2})$', time_str.strip())
        if match:
            h, m = int(match.group(1)), int(match.group(2))
            if 0 <= h <= 23 and 0 <= m <= 59:
                return time(h, m)
    except Exception:
        pass
    return None


@app.route("/add_schedule", methods=["GET", "POST"])
def add_schedule():
    form = AddScheduleForm()

    groups_duration = {}
    try:
        groups_data = api_request("/v1/groups/")
        groups_list = list(map(Group.from_dict, groups_data))

        form.group.choices = [
            (
                group.id,
                f'"{group.name_of_group}" с {get_full_teachers_initials_by_column(
                    Teacher.from_dict(api_request(
                        f'v1/teachers/{group.teacher_id}'))
                )}',
            )
            for group in groups_list
        ]

        for group in groups_list:
            duration_str = f"{group.duration.hour:02d}:{group.duration.minute:02d}:{group.duration.second:02d}"
            groups_duration[group.id] = duration_str

    except Exception as e:
        flash(f"Ошибка при загрузке групп: {str(e)}", "error")
        form.group.choices = []

    if form.validate_on_submit():
        schedule = Schedule()
        schedule.group_id = int(form.group.data)

        try:
            frequency_type = FrequencyType(form.frequency.data)
        except ValueError:
            flash("Неверный тип периодичности", "error")
            return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

        schedule.frequency = frequency_type

        ses = create_session()
        try:
            group = ses.get(Group, schedule.group_id)
            if not group:
                form.group.errors.append("Группа не найдена")
                return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

            duration = timedelta(
                hours=group.duration.hour,
                minutes=group.duration.minute,
                seconds=group.duration.second
            )

            target_date = None
            start_time_val = None

            if frequency_type == FrequencyType.SINGLE or frequency_type == FrequencyType.YEAR:
                dt = form.datetime.data
                if not dt:
                    form.datetime.errors.append("Укажите дату и время")
                    return render_template("add_schedule.html", form=form, groups_duration=groups_duration)
                target_date = dt.date()
                start_time_val = dt.time()

            elif frequency_type == FrequencyType.WEEK:
                weekday = form.weekday.data
                time_val = form.start_time.data

                if weekday is None:
                    form.weekday.errors.append("Выберите день недели")
                    return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

                if not time_val:
                    form.start_time.errors.append("Укажите время начала")
                    return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

                today = date.today()
                days_ahead = weekday - today.weekday()
                if days_ahead < 0:
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                start_time_val = time_val

            elif frequency_type == FrequencyType.MONTH:
                day = form.day_of_month.data
                time_val = form.start_time.data

                if not day:
                    form.day_of_month.errors.append("Укажите день месяца")
                    return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

                if not time_val:
                    form.start_time.errors.append("Укажите время начала")
                    return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

                import calendar
                today = date.today()
                max_days = calendar.monthrange(today.year, today.month)[1]

                if day > max_days:
                    form.day_of_month.errors.append(
                        f"В текущем месяце максимум {max_days} дней")
                    return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

                target_date = today.replace(day=day)
                start_time_val = time_val

            if not target_date or not start_time_val:
                flash("Ошибка определения даты или времени", "error")
                return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

            schedule.date = target_date
            schedule.start_time = start_time_val

            start_dt = datetime.combine(schedule.date, schedule.start_time)
            end_dt = start_dt + duration
            schedule.end_time = end_dt.time()

            if end_dt.date() != schedule.date:
                flash("Занятие заканчивается на следующий день", "error")
                return render_template("add_schedule.html", form=form, groups_duration=groups_duration)

            ses.add(schedule)
            ses.commit()
            flash("Событие успешно добавлено!", "success")
            return redirect(url_for('add_schedule'))

        except Exception as e:
            ses.rollback()
            flash(f"Произошла ошибка: {str(e)}", "error")
            import traceback
            traceback.print_exc()
        finally:
            ses.close()

    return render_template("add_schedule.html", form=form, groups_duration=groups_duration)


@app.route("/show_schedules")
def show_schedules():
    """Страница расписания"""
    group_id = request.args.get("group_id")
    id_and_group_names = api_request(
        "v1/groups", data={"fields": ["id", "name_of_group"]}, retries=1)

    print(f"\033[1;33m{id_and_group_names}\033[0m")

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

    # schedules = api_request("/v1/schedules/", retries=1)
    # print(schedules)
    # if not isinstance(schedules, tuple):
    #     schedules = [Schedule.from_dict(d)
    #                  for d in schedules]
    # else:
    #     schedules = []
    # if group_id:
    #     schedules = [s for s in schedules if s.group_id == int(group_id)]
    sess = create_session()
    stmt = select(Schedule)
    schedules = sess.scalars(stmt).all()
    unique_times = sorted(
        list(set(
            f'{s.start_time.strftime("%H:%M")}-{s.end_time.strftime("%H:%M")}' for s in schedules))
    )
    for _ in range(n_of_weeks):
        week_days_iso = [(current_week_start + timedelta(days=(d))
                          ).date().isoformat() for d in range(7)]
        days_lists.append(week_days_iso)

        matrix = []
        days_numerics = []
        for time_key in unique_times:
            row = [time_key]
            days_numerics = []
            for day_offset in range(7):
                cur_date = current_week_start + timedelta(days=day_offset)
                days_numerics.append(cur_date.day)
                events = []
                for s in schedules:
                    s_time = f'{s.start_time.strftime("%H:%M")}-{s.end_time.strftime("%H:%M")}'
                    if s_time == time_key and s.is_schedule_at_date(cur_date):
                        group_info = api_request(
                            f"/v1/groups/{s.group_id}", params={"fields": ["name_of_group", "id"]}, retries=1)
                        events.append(
                            {"title": group_info["name_of_group"], "id": s.id})
                row.append(events)
            matrix.append(row)

        week_end = current_week_start + timedelta(days=6)
        list_of_matrix_and_interval.append(
            (matrix, get_week_range(current_week_start, week_end), days_numerics))

        current_week_start += timedelta(days=7)

    next_date_str = current_week_start.strftime("%Y-%m-%d")
    print('---')
    print()
    print()
    print(list_of_matrix_and_interval)
    return render_template(
        "show_schedules_batch.html",
        list_of_matrix=list_of_matrix_and_interval,
        next_date=next_date_str,
        days_lists=days_lists,
    )
