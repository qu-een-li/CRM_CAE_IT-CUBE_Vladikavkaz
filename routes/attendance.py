from app import app
from flask import render_template, request, jsonify, url_for, redirect, abort
from data.schedule import Schedule
from data.direction import Direction
from itertools import zip_longest
from data.group_service import GroupService
from api.api_base import api_request
from data.student import Student
from data.past_schedules import PastSchedule
from config import API_HOST, API_PORT
from datetime import date
from babel.dates import format_date


@app.route("/attendance/create_past_schedule_if_doesnt_exist")
def create_past_schedule_if_doesnt_exist_and_redirect():
    """Создание списка учеников для определенного события и отмечивания их
      как не присутствующих по-умолчанию и перенаправление на форму
    изменения статуса присутствия определенного события"""
    schedule_id = request.args.get("schedule_id", type=int)
    date_str = request.args.get("date")
    if not all([schedule_id, date_str]):
        return "Missing parameters", 400
    schedule = Schedule.from_dict(api_request(f"v1/schedules/{schedule_id}"))

    past_date = date.fromisoformat(date_str)
    if not schedule.is_schedule_at_date(past_date):
        abort(404, message="schedule is not exist for that date.")
    past_schedule: dict = api_request(f"v1/past_schedules/schedule/{schedule_id}/date/{date_str}", retries=1)
    if isinstance(past_schedule, tuple) and past_schedule[0] is None:
        past_schedule = PastSchedule(schedule_id=schedule_id, date=past_date)
        new_past_schedule_dict = past_schedule.to_dict()
        del new_past_schedule_dict["id"]
        new_past_schedule_dict = api_request("v1/past_schedules/", data=new_past_schedule_dict, method="POST")
        past_schedule_id = new_past_schedule_dict["id"]
    else:
        past_schedule_id = past_schedule["id"]
    return redirect(url_for("add_or_change_students_check_in", past_schedule_id=past_schedule_id, str_date=date_str))


@app.route("/attendance/schedules/<int:past_schedule_id>/date/<str_date>/group/students_list")
def add_or_change_students_check_in(past_schedule_id: int, str_date: str):
    """Отображения формы для отметки присутсвующих на занятии"""
    formated_date = date.fromisoformat(str_date)

    formated_str_date = format_date(formated_date, format="full", locale="ru")
    past_schedule: dict = api_request(f"v1/past_schedules/{past_schedule_id}")
    schedule_id = past_schedule["schedule_id"]
    schedule = api_request(f"v1/schedules/{schedule_id}")
    group_id = schedule["group_id"]
    students: dict = api_request(
        f"/v1/past_schedules/{past_schedule_id}/students", params={"add_fields": ["were_present"]}
    )

    group: dict = api_request(f"v1/groups/{group_id}")
    return render_template(
        "add_or_change_students_check_in.html",
        group=group,
        students=students,
        past_schedule_id=past_schedule_id,
        current_date=formated_str_date,
    )


@app.route("/update_students_check_in/<int:past_schedule_id>", methods=["POST"])
def update_students_check_in(past_schedule_id):
    """Получаем все данные из формы, где мы отмечаем присутствие ученика на занятии и меняем данные, если ученик был"""
    data = request.get_json()  # { "student_id": false/true, "student_id": false/true ... }
    print(data)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    for student_id, is_present in data.items():
        print(
            api_request(
                f"v1/past_schedules/{past_schedule_id}/students/{student_id}",
                data={"were_present": is_present},
                method="PUT",
            )
        )

    return jsonify({"status": "success"}), 200
