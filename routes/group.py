from app import app
from flask import render_template, request, redirect, jsonify
from data import db_session
from data.group_service import GroupService


@app.route("/add_group", methods=["POST"])
def create_group():
    data = request.json
    session = db_session.create_session()

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
            description=data.get("description")
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
            description=data.get("description")
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
            description=data.get("description")
        )

        return jsonify({"success": True, "group_id": group.id, "lessons_count": len(group.schedule)})