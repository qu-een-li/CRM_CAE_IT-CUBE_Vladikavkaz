from app import app
from flask import render_template, request, jsonify
from data.db_session import create_session
from data.group import Group
from data.direction import Direction
from itertools import zip_longest
from data.group_service import GroupService
from api.api_base import api_request
from data.student import Student
from config import API_HOST, API_PORT


@app.route("/directions")
def list_directions():
    directions = [Direction.from_dict(direction)
                  for direction in api_request('v1/directions')]
    return render_template("directions.html", directions=directions)


@app.route("/direction/<int:direction_id>/groups")
def show_groups_from_direction(direction_id: int):
    direction = api_request(
        f'v1/directions/{direction_id}', params={'add_fields': ["groups"]})
    groups: list[Group] = [Group.from_dict(
        group) for group in direction['groups']]
    for group in groups:
        group.students = [Student.from_dict(
            student) for student in api_request(f'v1/groups/{group.id}/students')]
    direction = Direction.from_dict(direction)
    matrix = [[i.name_of_group for i in groups]]
    for row in zip_longest(*[i.students for i in groups], fillvalue=""):
        matrix.append(list(row))
    print(matrix)
    return render_template(
        "show_groups_of_direction.html", table_data=matrix, direction_name=direction.name, groups=groups, api_address=f"http://{API_HOST}:{API_PORT}/api/v1"
    )


@app.route("/add_group", methods=["POST"])
def create_group():
    data = request.json
    session = create_session()

    if data["group_type"] == "семестровый":
        group = GroupService.create_semester_group(
            session=session,
            name_of_group=data["name_of_group"],
            teacher_id=data["teacher_id"],
            direction_id=data["direction_id"],
            level_of_group=data["level_of_group"],
            study_period_id=data["study_period_id"],
            auditorium_id=data["auditorium_id"],
            first_lesson_date=data["first_lesson_date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            add_days=data.get("add_days", []),
            description=data.get("description"),
        )

    elif data["group_type"] == "интенсив":
        group = GroupService.create_intensive_group(
            session=session,
            name_of_group=data["name_of_group"],
            teacher_id=data["teacher_id"],
            direction_id=data["direction_id"],
            level_of_group=data["level_of_group"],
            study_period_id=data["study_period_id"],
            auditorium_id=data["auditorium_id"],
            custom_lessons=data["custom_lessons"],
            description=data.get("description"),
        )

    elif data["group_type"] == "мастер-класс":
        group = GroupService.create_masterclass_group(
            session=session,
            name_of_group=data["name_of_group"],
            teacher_id=data["teacher_id"],
            direction_id=data["direction_id"],
            level_of_group=data["level_of_group"],
            study_period_id=data["study_period_id"],
            auditorium_id=data["auditorium_id"],
            date=data["date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            description=data.get("description"),
        )

        return jsonify({"success": True, "group_id": group.id, "lessons_count": len(group.schedule)})
