from app import app
from flask import render_template, request, jsonify, redirect, url_for, flash
from data.db_session import create_session
from data.group import Group
from data.teacher import Teacher
from data.study_period import Study_period
from data.auditorium import Auditorium
from datetime import datetime, timedelta, date, time
from data.schedule import Schedule, FrequencyType
from data.direction import Direction
from data.student_in_group import student_in_group, StudentGroupStatus
from sqlalchemy import select, update, delete
from itertools import zip_longest
from data.group_service import GroupService
from api.api_base import api_request
from data.student import Student
from data.student_in_group import student_in_group
from config import API_HOST, API_PORT
from forms.groupform import GroupForm
from data.base_values import group_type_choices, is_weekly_group_type


@app.route("/directions")
def list_directions():
    """Отображения списка направлений"""
    directions = api_request("v1/directions")
    if not isinstance(directions, tuple):
        directions = [Direction.from_dict(direction)
                      for direction in directions]
    else:
        directions = []
    return render_template("directions.html", directions=directions)


@app.route("/direction/<int:direction_id>/groups")
def show_groups_from_direction(direction_id: int):
    """Отображения списка групп в направлении"""
    direction = api_request(
        f"v1/directions/{direction_id}", params={"add_fields": ["groups"]})
    groups: list[Group] = [Group.from_dict(
        group) for group in direction["groups"]]
    for group in groups:
        group.students = [Student.from_dict(student) for student in api_request(
            f"v1/groups/{group.id}/students")]
    direction = Direction.from_dict(direction)
    matrix = [[i.name_of_group for i in groups]]
    for row in zip_longest(*[i.students for i in groups], fillvalue=""):
        matrix.append(list(row))
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
    sess = create_session()
    group_data = api_request(f"v1/groups/{group_id}")
    students_data = api_request(f"v1/groups/{group_id}/students")

    # Преобразуем в объекты (если используете классы) или работаем со словарями
    group = Group.from_dict(group_data) if hasattr(
        Group, 'from_dict') else group_data
    students = []

    if hasattr(Student, 'from_dict'):
        today = date.today()
        for student in students_data:
            student = Student.from_dict(student)
            if student.birthday is not None:
                student.age = (today.year
                               - student.birthday.year
                               - ((today.month, today.day) <
                                  (student.birthday.month, student.birthday.day))
                               )
            link = sess.execute(
                select(student_in_group.c.is_order, student_in_group.c.status).where(
                    student_in_group.c.student_id == student.id, student_in_group.c.group_id == group.id)
            ).first()
            student.is_order = link.is_order if link else False
            student.group_status = StudentGroupStatus(link.status) if link else StudentGroupStatus.STUDENT
            # в каких ещё группах учится ученик (один ученик может быть в разных группах)
            student.other_groups = sess.execute(
                select(Group.id, Group.name_of_group)
                .join(student_in_group, student_in_group.c.group_id == Group.id)
                .where(student_in_group.c.student_id == student.id, Group.id != group.id)
            ).all()
            students.append(student)
    else:
        students = students_data

    # группы для перевода ученика (кроме текущей), сгруппированы по направлениям
    all_groups = sess.query(Group).filter(Group.id != group_id).order_by(Group.direction_id, Group.name_of_group).all()
    transfer_groups = {}
    for g in all_groups:
        transfer_groups.setdefault(g.direction.name if g.direction else "Без направления", []).append(
            {"id": g.id, "name": g.name_of_group})

    return render_template(
        "show_group_details.html",
        group=group,
        students=students,
        statuses=list(StudentGroupStatus),
        transfer_groups=transfer_groups,
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
    teachers = session.query(Teacher).all()
    directions = session.query(Direction).all()
    study_periods = session.query(Study_period).order_by(Study_period.id).all()
    auditories = session.query(Auditorium).all()
    form.teachers.choices = [('', 'Выберите учителя')] + [
        (str(teacher.id), teacher.get__teachers_patronymic()) for teacher in teachers]
    form.directions.choices = [('', 'Выберите направление')] + [
        (str(direction.id), direction.name) for direction in directions]
    form.study_periods.choices = [('', 'Выберите период обучения')] + [
        (str(study_period.id), study_period.reporting_period) for study_period in study_periods]
    form.auditories.choices = [('', 'Выберите аудиторию')] + [
        (str(auditory.id), auditory.name) for auditory in auditories]
    form.group_type.choices = group_type_choices()

    if request.method == 'GET':
        # по умолчанию — текущий (последний добавленный) учебный период
        if study_periods:
            form.study_periods.data = str(study_periods[-1].id)
        # после добавления наставника по кнопке "+" сразу выбираем его
        new_teacher_id = request.args.get('teacher_id')
        if new_teacher_id:
            form.teachers.data = new_teacher_id

    if form.validate_on_submit():
        period = session.get(Study_period, int(form.study_periods.data))
        start_dt = form.start_datetime.data
        hours, minutes = map(int, form.duration.data.split(':'))
        duration = timedelta(hours=hours, minutes=minutes)
        end_dt = start_dt + duration

        if not (period.date_start <= start_dt.date() <= period.date_end):
            form.start_datetime.errors.append(
                f"Дата первого занятия должна быть внутри учебного периода "
                f"({period.date_start:%d.%m.%Y} – {period.date_end:%d.%m.%Y})")
        elif end_dt.date() != start_dt.date():
            form.start_datetime.errors.append("Занятие не может заканчиваться на следующий день")
        else:
            group = Group(
                name_of_group=form.name.data.strip(),
                teacher_id=int(form.teachers.data),
                direction_id=int(form.directions.data),
                study_period_id=period.id,
                level_of_education=form.levels_of_education.data,
                group_type=form.group_type.data,
                description=form.description.data,
                duration=time(hours, minutes),
                first_lesson_date=start_dt.date(),
            )
            session.add(group)
            session.flush()

            # первое занятие: у "еженедельных" типов (настройка weekly в base_values.json) повторяется
            # каждую неделю, у остальных — разовое событие (следующие занятия добавляются в /add_schedule)
            frequency = FrequencyType.WEEK if is_weekly_group_type(group.group_type) else FrequencyType.SINGLE
            session.add(Schedule(
                group_id=group.id,
                date=start_dt.date(),
                start_time=start_dt.time(),
                end_time=end_dt.time(),
                auditorium_id=int(form.auditories.data),
                frequency=frequency,
            ))
            session.commit()
            flash(f"Группа «{group.name_of_group}» создана", "success")
            return redirect('/')
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


def parse_group_status(value, default=StudentGroupStatus.STUDENT):
    """Статус из запроса: число (0/1) или название ('student'/'candidate')"""
    if value is None or value == "":
        return default
    try:
        return StudentGroupStatus(int(value))
    except (ValueError, TypeError):
        pass
    try:
        return StudentGroupStatus[str(value).upper()]
    except KeyError:
        return None


def get_group_link(ses, group_id, student_id):
    return ses.execute(
        select(student_in_group).where(
            student_in_group.c.group_id == group_id, student_in_group.c.student_id == student_id)
    ).first()


def put_student_in_group(ses, group_id, student_id, status=StudentGroupStatus.STUDENT):
    """Добавляет ученика в группу. Ученик может быть в нескольких группах, но в одной — только один раз.
    Возвращает False, если он уже в этой группе."""
    if get_group_link(ses, group_id, student_id):
        return False
    ses.execute(student_in_group.insert().values(
        group_id=group_id, student_id=student_id, is_order=False, status=int(status)))
    return True


@app.route('/group/<int:group_id>/add/student/<int:student_id>', methods=['POST'])
def add_student_to_group(group_id, student_id):
    ses = create_session()

    if not ses.get(Group, group_id):
        return jsonify({'error': 'Группа не найдена'}), 404
    if not ses.get(Student, student_id):
        return jsonify({'error': 'Ученик не найден'}), 404

    data = request.get_json(silent=True) or {}
    status = parse_group_status(data.get('status'))
    if status is None:
        return jsonify({'error': 'Неизвестный статус'}), 400

    if not put_student_in_group(ses, group_id, student_id, status):
        return jsonify({'error': 'Ученик уже есть в этой группе'}), 409
    ses.commit()
    return jsonify({'message': 'Ученик добавлен в группу'}), 200


@app.route('/groups/<int:group_id>/<int:student_id>', methods=['DELETE'])
def remove_student_from_group(group_id, student_id):
    """Удаление ученика из группы (сам ученик в базе остаётся)"""
    ses = create_session()
    result = ses.execute(delete(student_in_group).where(
        student_in_group.c.group_id == group_id, student_in_group.c.student_id == student_id))
    ses.commit()
    if result.rowcount == 0:
        return jsonify({'error': 'Ученика нет в этой группе'}), 404
    return jsonify({'message': 'Ученик удалён из группы'}), 200


@app.route('/groups/<int:group_id>/<int:student_id>/status', methods=['POST'])
def change_student_group_status(group_id, student_id):
    """Изменение статуса ученика в группе: кандидат / ученик"""
    ses = create_session()
    data = request.get_json(silent=True) or {}
    status = parse_group_status(data.get('status'), default=None)
    if status is None:
        return jsonify({'error': 'Неизвестный статус'}), 400

    result = ses.execute(update(student_in_group).where(
        student_in_group.c.group_id == group_id, student_in_group.c.student_id == student_id
    ).values(status=int(status)))
    ses.commit()
    if result.rowcount == 0:
        return jsonify({'error': 'Ученика нет в этой группе'}), 404
    return jsonify({'message': 'Статус изменён', 'status': int(status), 'title': status.title}), 200


@app.route('/groups/<int:group_id>/<int:student_id>/transfer', methods=['POST'])
def transfer_student_to_group(group_id, student_id):
    """Перевод ученика в другую группу: статус сохраняется, приказ — нет (он издаётся на конкретную группу)"""
    ses = create_session()
    data = request.get_json(silent=True) or {}
    try:
        to_group_id = int(data.get('to_group_id'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Не выбрана группа для перевода'}), 400

    if to_group_id == group_id:
        return jsonify({'error': 'Ученик уже в этой группе'}), 400
    if not ses.get(Group, to_group_id):
        return jsonify({'error': 'Группа не найдена'}), 404

    link = get_group_link(ses, group_id, student_id)
    if not link:
        return jsonify({'error': 'Ученика нет в текущей группе'}), 404
    if not put_student_in_group(ses, to_group_id, student_id, StudentGroupStatus(link.status)):
        return jsonify({'error': 'Ученик уже есть в выбранной группе'}), 409

    ses.execute(delete(student_in_group).where(
        student_in_group.c.group_id == group_id, student_in_group.c.student_id == student_id))
    ses.commit()
    return jsonify({'message': 'Ученик переведён', 'to_group_id': to_group_id}), 200


MONTHS_NOMINATIVE = ["январь", "февраль", "март", "апрель", "май", "июнь",
                     "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]


@app.route('/study_periods/add', methods=['POST'])
def add_study_period():
    """Создание учебного периода (из модального окна на странице создания группы)"""
    data = request.get_json(silent=True) or {}
    try:
        date_start = datetime.strptime(data.get("date_start", ""), "%Y-%m-%d").date()
        date_end = datetime.strptime(data.get("date_end", ""), "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"success": False, "error": "Укажите корректные даты начала и конца периода"}), 400
    if date_end <= date_start:
        return jsonify({"success": False, "error": "Дата конца должна быть позже даты начала"}), 400

    # название вида "сентябрь 2026 - февраль 2027"
    name = (data.get("reporting_period") or "").strip()
    if not name:
        name = (f"{MONTHS_NOMINATIVE[date_start.month - 1]} {date_start.year} - "
                f"{MONTHS_NOMINATIVE[date_end.month - 1]} {date_end.year}")

    session = create_session()
    exists = session.query(Study_period).filter(
        Study_period.date_start == date_start, Study_period.date_end == date_end).first()
    if exists:
        return jsonify({"success": False, "error": f"Такой период уже есть: {exists.reporting_period}"}), 400

    period = Study_period(reporting_period=name, date_start=date_start, date_end=date_end)
    session.add(period)
    session.commit()
    return jsonify({"success": True, "id": period.id, "reporting_period": period.reporting_period})
