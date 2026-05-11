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


@app.route('/attendance/create_past_schedule_if_doesnt_exist')
def create_past_schedule_if_doesnt_exist_and_redirect():
    past_schedule_id = request.args.get('past_schedule_id', type=int)
    schedule_id = request.args.get('schedule_id', type=int)
    date_str = request.args.get('date')
    schedule = Schedule.from_dict(api_request(f'v1/schedules/{schedule_id}'))
    if not all([past_schedule_id, schedule_id, date_str]):
        return "Missing parameters", 400

    past_date = date.fromisoformat(date_str)
    if not schedule.is_schedule_at_date(past_date):
        abort(404, message='schedule is not exist for that date.')
    past_schedule: dict = api_request(
        f'v1/past_schedules/{past_schedule_id}')
    if not past_schedule:
        past_schedule = PastSchedule(
            id=past_schedule_id, schedule_id=schedule_id, data=past_date)
        api_request('v1/past_schedules/',
                    data=past_schedule.to_dict(), method='POST')

    redirect(url_for('add_or_change_students_check_in',
             past_schedule_id=past_schedule_id))


@app.route('/attendance/schedules/<int:past_schedule_id>/group/students_list')
def add_or_change_students_check_in(past_schedule_id: int):
    past_schedule: dict = api_request(
        f'v1/past_schedules/{past_schedule_id}')
    print(past_schedule)
    schedule_id = past_schedule['schedule_id']
    schedule = api_request(f'v1/schedules/{schedule_id}')
    group_id = schedule['group_id']
    students: dict = api_request(f'v1/groups/{group_id}/students')
    group: dict = api_request(f'v1/groups/{group_id}')
    render_template('add_or_change_students_check_in.html', group=group,
                    students=students, past_schedule_id=past_schedule_id)
