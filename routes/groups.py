from app import app
from flask import render_template, request, jsonify
from data.db_session import create_session
from data.group import Group
from data.direction import Direction
from itertools import zip_longest
from data.group_service import GroupService
from flask_login import login_required
from data.student import Student


@app.route("/directions")
def list_directions():
    db_sess = create_session()
    directions = db_sess.query(Direction).all()
    return render_template("directions.html", directions=directions)


@app.route("/direction/<int:direction_id>/groups")
def show_groups_from_direction(direction_id: int):
    db_sess = create_session()
    direction = db_sess.get(Direction, direction_id)
    groups: list[Group] = direction.groups
    matrix = [[i.name_of_group for i in groups]]
    for row in zip_longest(*[i.students for i in groups], fillvalue=""):
        matrix.append(list(row))
    return render_template(
        "show_groups_of_direction.html", table_data=matrix, direction_name=direction.name, groups=direction.groups
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


@app.route("/groups/<int:group_id>/<int:student_id>", methods=["DELETE"])
def delete_student(group_id, student_id):
    db_session = create_session()
    group = db_session.get(Group, group_id)
    student = db_session.get(Student, student_id)

    # 2. Проверяем, что оба объекта существуют
    if not group or not student:
        return jsonify({"error": "Группа или студент не найдены"}), 404

    try:
        # 3. Удаляем связь (предполагается, что в модели Group есть relationship 'students')
        if student in group.students:
            group.students.remove(student)
            db_session.commit()
            return "", 204  # Успех, без тела ответа
        else:
            return jsonify({"error": "Студент не состоит в этой группе"}), 400

    except Exception as e:
        db_session.rollback()  # Откатываем в случае ошибки
        return jsonify({"error": str(e)}), 500


@app.route("/groups/<int:group_id>/<int:student_id>", methods=["POST"])
def add_student(group_id, student_id):
    db_session = create_session()
    group = db_session.get(Group, group_id)
    student = db_session.get(Student, student_id)

    # 2. Проверяем, что оба объекта существуют
    if not group or not student:
        return jsonify({"error": "Группа или студент не найдены"}), 404

    try:
        # 3. Удаляем связь (предполагается, что в модели Group есть relationship 'students')
        if student not in group.students:
            group.students.append(student)
            db_session.commit()
            return "", 204  # Успех, без тела ответа
        else:
            return jsonify({"error": "Студент итак состоит в этой группе"}), 400

    except Exception as e:
        db_session.rollback()  # Откатываем в случае ошибки
        return jsonify({"error": str(e)}), 500
