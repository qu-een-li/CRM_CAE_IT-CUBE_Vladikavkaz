from app import app
from flask import render_template, request, jsonify, redirect, url_for
from data.db_session import create_session
from data.group import Group
from data.teacher import Teacher
from data.study_period import Study_period
from data.auditorium import Auditorium
from datetime import datetime, timedelta
from data.direction import Direction
from data.student_in_group import student_in_group

from itertools import zip_longest
from data.group_service import GroupService
from api.api_base import api_request
from data.student import Student
from config import API_HOST, API_PORT
from forms.groupform import GroupForm


@app.route("/directions")
def list_directions():
    """Отображения списка направлений"""

    directions = [Direction.from_dict(direction)
                  for direction in api_request("v1/directions")]
    return render_template("directions.html", directions=directions)


@app.route("/direction/<int:direction_id>/groups")
def show_groups_from_direction(direction_id: int):
    """Отображения списка групп в направлении"""
    direction = api_request(
        f"v1/directions/{direction_id}", params={"add_fields": ["groups"]})
    print(direction)
    groups: list[Group] = [Group.from_dict(
        group) for group in direction["groups"]]
    for group in groups:
        group.students = [Student.from_dict(student) for student in api_request(
            f"v1/groups/{group.id}/students")]
    direction = Direction.from_dict(direction)
    matrix = [[i.name_of_group for i in groups]]
    for row in zip_longest(*[i.students for i in groups], fillvalue=""):
        matrix.append(list(row))
    print(matrix)
    return render_template(
        "show_groups_of_direction.html",
        table_data=matrix,
        direction_name=direction.name,
        groups=groups,
        api_address=f"http://{API_HOST}:{API_PORT}/api/v1",
    )


@app.route("/groups/<int:group_id>")
def show_group_details(group_id: int):
    """Отображение списка участников конкретной группы"""

    # Получаем данные о группе и студентах через API
    group_data = api_request(f"v1/groups/{group_id}")
    students_data = api_request(f"v1/groups/{group_id}/students")

    # Преобразуем в объекты (если используете классы) или работаем со словарями
    group = Group.from_dict(group_data) if hasattr(
        Group, 'from_dict') else group_data
    students = [Student.from_dict(s) for s in students_data] if hasattr(
        Student, 'from_dict') else students_data

    # Формируем адрес API для JS (как и в предыдущем примере)
    api_url = f"http://{API_HOST}:{API_PORT}/api/v1"

    return render_template(
        "show_group_details.html",
        group=group,
        students=students,
    )
# @app.route("/create_group", methods=["POST"])
# def add_group():
#     """создание группы"""

#     data = request.json
    # session = create_session()

    # if data["group_type"] == "семестровый":
    #     group = GroupService.create_semester_group(
    #         session=session,
    #         name_of_group=data["name_of_group"],
    #         teacher_id=data["teacher_id"],
    #         direction_id=data["direction_id"],
    #         level_of_group=data["level_of_group"],
    #         study_period_id=data["study_period_id"],
    #         auditorium_id=data["auditorium_id"],
    #         first_lesson_date=data["first_lesson_date"],
    #         start_time=data["start_time"],
    #         end_time=data["end_time"],
    #         add_days=data.get("add_days", []),
    #         description=data.get("description"),
    #     )

    # elif data["group_type"] == "интенсив":
    #     group = GroupService.create_intensive_group(
    #         session=session,
    #         name_of_group=data["name_of_group"],
    #         teacher_id=data["teacher_id"],
    #         direction_id=data["direction_id"],
    #         level_of_group=data["level_of_group"],
    #         study_period_id=data["study_period_id"],
    #         auditorium_id=data["auditorium_id"],
    #         custom_lessons=data["custom_lessons"],
    #         description=data.get("description"),
    #     )

    # elif data["group_type"] == "мастер-класс":
    #     group = GroupService.create_masterclass_group(
    #         session=session,
    #         name_of_group=data["name_of_group"],
    #         teacher_id=data["teacher_id"],
    #         direction_id=data["direction_id"],
    #         level_of_group=data["level_of_group"],
    #         study_period_id=data["study_period_id"],
    #         auditorium_id=data["auditorium_id"],
    #         date=data["date"],
    #         start_time=data["start_time"],
    #         end_time=data["end_time"],
    #         description=data.get("description"),
    #     )

#         return jsonify({"success": True, "group_id": group.id, "lessons_count": len(group.schedule)})


@app.route('/add_group', methods=['GET', 'POST'])
def add_empty_group():
    form = GroupForm()
    session = create_session()
    data = request.form.to_dict()
    teachers = session.query(Teacher).all()
    directions = session.query(Direction).all()
    study_periods = session.query(Study_period).all()
    auditories = session.query(Auditorium).all()
    form.teachers.choices = [
        (teacher.id, teacher.get__teachers_patronymic()) for teacher in teachers]
    form.directions.choices = [(direction.id, direction.name)
                               for direction in directions]
    form.study_periods.choices = [
        (study_period.id, study_period.reporting_period) for study_period in study_periods]
    form.auditories.choices = [(auditory.id, auditory.name)
                               for auditory in auditories]
    if form.validate_on_submit():
        group = Group()
        group.name_of_group = form.name.data
        group.teacher_id = form.teachers.data
        group.direction_id = form.directions.data
        group.study_period_id = form.study_periods.data
        group.auditorium_id = form.auditories.data
        group.level_of_education = form.levels_of_education.data
        group.group_type = 'семестровый'
        group.description = form.description.data
        group.duration = form.duration.data
        session.add(group)
        session.commit()
        print(group.direction_id)
        print("Данные для создания группы:", data)
        return redirect(url_for('show_group_details', group_id=group.id))
    return render_template('add_group.html', form=form)


@app.route("/students/search")
def search_students():
    """Поиск студентов по имени"""
    query_param = request.args.get('q', '')
    print('q =', query_param)
    if not query_param or len(query_param) < 2:
        return jsonify([])

    session = create_session()
    from sqlalchemy import func

    students = session.query(Student).filter(
        func.lower(Student.name_student).like(f'%{query_param.lower()}%')
    ).limit(20).all()

    result = [
        {
            'id': student.id,
            'name_student': student.name_student,
            'full_name': student.name_student
        }
        for student in students
    ]
    print(result)
    return jsonify(result)


@app.route('/group/<int:group_id>/add/student/<int:student_id>', methods=['POST'])
def add_student_to_group(group_id, student_id):
    print('добавление пользователя в группу')
    ses = create_session()

    group = ses.get(Group, group_id)
    student = ses.get(Student, student_id)

    if not group:
        return jsonify({'error': 'Group not found'}), 404
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if student in group.students:
        return jsonify({'message': 'Student already in group'}), 200

    group.students.append(student)
    ses.commit()
    return jsonify({'message': 'Student added to group'}), 200
