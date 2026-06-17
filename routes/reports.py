import pandas as pd
from data.db_session import create_session
from data.teacher import Teacher
from data.direction import Direction
from data.group import Group
from data.student import Student
from data.past_schedules import PastSchedule
from data.students_to_past_schedule import Student_to_past_schedule
from data.schedule import Schedule
from app import app
import io
from flask import send_file, request, flash, redirect, render_template, url_for, abort
from datetime import datetime
import calendar
from babel.dates import format_date


@app.route('/reports')
def reports_page():
    """Главная страница репортов"""
    ses = create_session()
    teachers = ses.query(Teacher).all()
    for teacher in teachers:
        if teacher.patronymic:
            teacher.fio = f"{teacher.surename} {teacher.name[0]}.{teacher.patronymic[0]}.".title(
            )
        else:
            teacher.fio = f"{teacher.surename} {teacher.name[0]}.".title()
    groups = ses.query(Group).all()
    return render_template("reports.html", teachers=teachers, groups=groups)


def create_attendance_report(teacher_name, course_name, period_start, period_end, students_data):
    """Отчет успеваемости учеников преподавателя."""
    output = io.BytesIO()
    if not students_data:
        students_data = [
            {
                "student": "Ни одного студента",
                "total_number": 0,
                "total": 0,
                "percent_skipped": 0,
            }
        ]
    df = pd.DataFrame(students_data)
    df.columns = [
        "ФИО обучающегося",
        "Суммарно количество занятий за период в соответствии с календарно-тематическим планом",
        "Суммарно посещенных занятий за период",
        "% пропущенных занятий",
    ]
    # Добавляем индекс (№ п/п)
    df.index = range(1, len(df) + 1)
    df.index.name = "№ п/п"
    df = df.reset_index()

    # Начинаем запись в Excel
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    workbook = writer.book
    worksheet = workbook.add_worksheet("Посещаемость")

    # Настройки форматов
    header_format = workbook.add_format(
        {"bold": True, "align": "center", "valign": "vcenter", "font_size": 14})
    table_header_format = workbook.add_format(
        {"border": 1, "align": "center", "valign": "vcenter", "text_wrap": True})
    cell_format = workbook.add_format(
        {"border": 1, "align": "left", "valign": "vcenter"})
    num_format = workbook.add_format(
        {"border": 1, "align": "right", "valign": "vcenter"})

    worksheet.merge_range(
        "B1:F1", "Сводная ведомость учета посещаемости", header_format)

    worksheet.write("A2", "направление:")
    worksheet.merge_range("C2:D3", course_name, cell_format)
    worksheet.write("E2", "педагог")
    worksheet.write("F2", teacher_name, workbook.add_format({"bottom": 1}))

    worksheet.write("A4", "за период")
    worksheet.write("C4", period_start, workbook.add_format({"bold": True}))
    worksheet.write("D4", f"по {period_end}")
    worksheet.write("E4", "года")

    for col_num, value in enumerate(df.columns.values):
        worksheet.write(4, col_num + 1, value, table_header_format)

    percent_fmt = workbook.add_format(
        {"border": 1, "num_format": "0%", "align": "right"})
    srednaya_percent = 0
    for row_num, row_data in enumerate(df.values):
        for col_num, cell_value in enumerate(row_data):

            if col_num == 4:
                val = cell_value / 100
                srednaya_percent += float(val)
                current_fmt = percent_fmt
            else:
                val = cell_value
                current_fmt = cell_format if col_num <= 1 else num_format

            worksheet.write(row_num + 5, col_num + 1, val, current_fmt)

    worksheet.set_column("A:A", 5)
    worksheet.set_column("B:B", 6)
    worksheet.set_column("C:C", 30)
    worksheet.set_column("D:D", 20)
    worksheet.set_column("E:E", 15)
    worksheet.set_column("F:F", 15)
    footer_row = 5 + len(df) + 1
    worksheet.write(footer_row, 2, "Количество обучающихся:", cell_format)
    worksheet.write(footer_row, 3, str(len(students_data)))
    worksheet.write(footer_row + 1, 2,
                    "Процент пропущенных занятий составляет:")
    srednaya_percent /= len(students_data)
    worksheet.write(footer_row + 1, 3, str(int((srednaya_percent) * 100)))

    writer.close()
    output.seek(0)
    print(f"Файл {output} успешно создан!")
    return output


@app.route("/reports/teacher/<int:teacher_id>/attendance/students")
def route_view_teachers_students_attendance(teacher_id: int):
    """Просмотр отчета успеваемости учеников в формате HTML."""

    # 1. Получение параметров дат (копия вашей логики)
    start_month_str = request.args.get("start_date")
    end_month_str = request.args.get("end_date")

    start_date = None
    end_date = None

    if start_month_str:
        start_date = datetime.strptime(start_month_str, "%Y-%m").date()
    if end_month_str:
        temp_date = datetime.strptime(end_month_str, "%Y-%m").date()
        last_day = calendar.monthrange(temp_date.year, temp_date.month)[1]
        end_date = temp_date.replace(day=last_day)

    if start_date and end_date and start_date >= end_date:
        flash("Дата начала не может быть позже даты конца.", "error")
        return redirect(request.referrer or "/")

    # 2. Сбор данных из БД (копия вашей логики)
    ses = create_session()
    teacher = ses.get(Teacher, teacher_id)
    if not teacher:
        abort(404, description="Преподаватель не найден")

    if teacher.patronymic:
        formatted_teacher_name = f"{teacher.surename} {teacher.name[0]}.{teacher.patronymic[0]}.".title(
        )
    else:
        formatted_teacher_name = f"{teacher.surename} {teacher.name[0]}.".title(
        )

    groups = ses.query(Group).filter_by(teacher_id=teacher_id).all()
    directions = []
    students = {}
    schedules = []

    for group in groups:
        if group.direction not in directions:
            directions.append(group.direction)
        for schedule in group.schedules:
            if schedule not in schedules:
                schedules.append(schedule)
                for past_schedule in ses.query(PastSchedule).filter_by(schedule_id=schedule.id).all():
                    if start_date and past_schedule.date < start_date:
                        continue
                    if end_date and past_schedule.date > end_date:
                        continue
                    for student in past_schedule.students:
                        if student.name_student not in students:
                            students[student.name_student] = [0, 0]
                        students[student.name_student][1] += 1

                        is_present = ses.query(Student_to_past_schedule).filter_by(
                            student_id=student.id,
                            past_schedule_id=past_schedule.id
                        ).first().were_present

                        students[student.name_student][0] += 1 if is_present else 0

    # 3. Форматирование строк направлений (копия вашей логики)
    courses = ""
    if len(directions):
        if len(directions) == 1:
            courses = directions[0].name
        else:
            courses = ", ".join(
                [direction.name for direction in directions[:-1]])
            courses += f" и {directions[-1].name}"
        courses = courses.title()

    # 4. Формирование списка студентов и расчет среднего %
    students_list = []
    srednaya_percent = 0

    for student_name, (total_number, total) in students.items():
        percent_skipped = 100 - int(round(total_number / total, 2) * 100)
        srednaya_percent += (percent_skipped / 100)
        students_list.append({
            "name": student_name,
            "total_number": total_number,
            "total": total,
            "percent_skipped": percent_skipped
        })

    # Расчет финальных показателей для подвала таблицы
    total_students = len(students_list)
    avg_skipped_percent = int(
        (srednaya_percent / total_students) * 100) if total_students > 0 else 0

    # Форматирование дат для заголовка
    period_start_formatted = format_date(
        start_date, format="MMM y", locale="ru_RU") if start_date else "♾️"
    period_end_formatted = format_date(
        end_date, format="MMM y", locale="ru_RU") if end_date else "♾️"

    # Сохраняем query-параметры, чтобы кнопка «Скачать» знала, за какой период выгружать Excel
    download_url = url_for(
        'route_to_create_teachers_students_attendance', teacher_id=teacher_id, **request.args)

    return render_template(
        "attendance_report.html",
        teacher_name=formatted_teacher_name,
        course_name=courses.capitalize(),
        period_start=period_start_formatted,
        period_end=period_end_formatted,
        students=students_list,
        total_students=total_students,
        avg_skipped_percent=avg_skipped_percent,
        download_url=download_url
    )


@app.route("/reports/teacher/<int:teacher_id>/attendance/students/download")
def route_to_create_teachers_students_attendance(teacher_id: int):
    """route для отчета успеваемости учеников преподавателя."""

    start_month_str = request.args.get("start_date")  # придет "2025-09"
    end_month_str = request.args.get("end_date")  # придет "2026-01"

    start_date = None
    end_date = None

    if start_month_str:
        # Конвертируем в 1-е число указанного месяца
        start_date = datetime.strptime(start_month_str, "%Y-%m").date()

    if end_month_str:
        # Находим последний день указанного месяца
        temp_date = datetime.strptime(end_month_str, "%Y-%m").date()
        last_day = calendar.monthrange(temp_date.year, temp_date.month)[1]
        end_date = temp_date.replace(day=last_day)
    if start_date and end_date:
        if start_date >= end_date:
            flash("Дата начала не может быть позже даты конца.", "error")
            # Возвращаем пользователя на ту же страницу, не продолжая выполнение функции
            return redirect(request.referrer or "/")
    ses = create_session()
    teacher = ses.get(Teacher, teacher_id)
    if teacher.patronymic:
        formatted_teacher_name = f"{teacher.surename} {teacher.name[0]}.{teacher.patronymic[0]}.".title(
        )
    else:
        formatted_teacher_name = f"{teacher.surename} {teacher.name[0]}.".title(
        )
    groups = ses.query(Group).filter_by(teacher_id=teacher_id).all()
    directions: list[Direction] = []
    students: dict[str, list[int, int]] = {}
    schedules: list[Schedule] = []
    for group in groups:
        if group.direction not in directions:
            directions.append(group.direction)
        for schedule in group.schedules:
            if schedule not in schedules:
                schedules.append(schedule)
                for past_schedule in ses.query(PastSchedule).filter_by(schedule_id=schedule.id).all():
                    if start_date:
                        if past_schedule.date < start_date:
                            continue
                    if end_date:
                        if past_schedule.date > end_date:
                            continue
                    for student in past_schedule.students:
                        student: Student
                        if student.name_student not in students:
                            students[student.name_student] = [0, 0]
                        students[student.name_student][1] += 1
                        students[student.name_student][0] += (
                            1
                            if ses.query(Student_to_past_schedule)
                            .filter_by(student_id=student.id, past_schedule_id=past_schedule.id)
                            .first()
                            .were_present
                            else 0
                        )
    courses = ""
    if len(directions):
        if len(directions) == 1:
            courses = directions[0].name
        else:
            courses = ", ".join(
                [direction.name for direction in directions[:-1]])
            courses += f" и {directions[-1].name}"
        courses = courses.title()

    data = []
    for student_name, (total_number, total) in students.items():
        data.append(
            {
                "student": student_name,
                "total_number": total_number,
                "total": total,
                "percent_skipped": 100 - int(round(total_number / total, 2) * 100),
            }
        )
    excel_file = create_attendance_report(
        formatted_teacher_name,
        courses.capitalize(),
        format_date(start_date, format="MMM y",
                    locale="ru_RU") if start_date else "♾️",
        format_date(end_date, format="MMM y",
                    locale="ru_RU") if end_date else "♾️",
        data,
    )
    return send_file(
        excel_file,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="attendance_report.xlsx",
    )


# посещаемость по группам


def create_attendance_report_group(students_names: list[str], attendance_dict: dict[str, list[str]]):
    """Отчет успеваемости учеников группы."""
    # Создаем DataFrame
    df = pd.DataFrame(index=students_names)

    for date, attended_students in attendance_dict.items():
        df[date] = df.index.map(
            lambda name: "V" if name in attended_students else "X")

    df.sort_index(inplace=True)

    output = io.BytesIO()

    # Используем xlsxwriter для кастомизации
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Посещаемость")

        workbook = writer.book
        worksheet = writer.sheets["Посещаемость"]

        # 1. Определяем форматы (цвета и стили)
        format_v = workbook.add_format(
            {"bg_color": "#C6EFCE", "font_color": "#006100",
                "align": "center", "border": 1}
        )  # Светло-зеленый
        format_x = workbook.add_format(
            {"bg_color": "#FFC7CE", "font_color": "#9C0006",
                "align": "center", "border": 1}
        )  # Розовый
        format_header = workbook.add_format(
            {"bold": True, "bg_color": "#4F81BD",
                "font_color": "white", "border": 1, "align": "center"}
        )

        # 2. Условное форматирование для всей таблицы данных
        # (Начинаем с ячейки B2, так как A - это имена, 1 - это даты)
        rows = len(df)
        cols = len(df.columns)

        # Задаем ширину первой колонки (имена)
        worksheet.set_column(0, 0, 25)
        # Задаем ширину колонок с датами
        worksheet.set_column(1, cols, 12)

        # Применяем правила: если "V", то зеленый, если "X", то красный
        worksheet.conditional_format(
            1, 1, rows, cols, {
                "type": "cell", "criteria": "equal to", "value": '"V"', "format": format_v}
        )

        worksheet.conditional_format(
            1, 1, rows, cols, {
                "type": "cell", "criteria": "equal to", "value": '"X"', "format": format_x}
        )

        # 3. Принудительно красим заголовки (даты и заголовок имен)
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num + 1, value, format_header)
        worksheet.write(0, 0, "ФИО Студента", format_header)

    output.seek(0)
    print(f"Цветной отчет сформирован. Записей: {len(df)}")
    return output


@app.route("/reports/group/<int:group_id>/attendance/students")
def route_to_create_group_students_attendance(group_id: int):
    """Роут для веб-отображения отчета посещаемости учеников группы."""
    start_month_str = request.args.get("start_date")  # придет "2025-09"
    end_month_str = request.args.get("end_date")    # придет "2026-01"

    start_date = None
    end_date = None

    if start_month_str:
        start_date = datetime.strptime(start_month_str, "%Y-%m").date()

    if end_month_str:
        temp_date = datetime.strptime(end_month_str, "%Y-%m").date()
        last_day = calendar.monthrange(temp_date.year, temp_date.month)[1]
        end_date = temp_date.replace(day=last_day)

    if start_date and end_date:
        if start_date >= end_date:
            flash("Дата начала не может быть позже даты конца.", "error")
            return redirect(request.referrer or "/")

    ses = create_session()
    group = ses.get(Group, group_id)
    if not group:
        abort(404, description="Группа не найдена")

    students = group.students
    schedules = group.schedules

    # Сбор прошедших занятий
    past_schedules: list[PastSchedule] = []
    for schedule in schedules:
        # Добавляем фильтрацию по датам, чтобы не выгружать лишнее в HTML
        query = ses.query(PastSchedule).filter_by(schedule_id=schedule.id)
        if start_date:
            query = query.filter(PastSchedule.date >= start_date)
        if end_date:
            query = query.filter(PastSchedule.date <= end_date)
        past_schedules += query.all()

    dates: dict[str, list[str]] = {}
    for past_schedule in past_schedules:
        date = past_schedule.date
        dates[date] = []
        for student in past_schedule.students:
            student_to_past_schedule = (
                ses.query(Student_to_past_schedule)
                .filter_by(past_schedule_id=past_schedule.id, student_id=student.id)
                .first()
            )
            if not student_to_past_schedule or not student_to_past_schedule.were_present or student not in students:
                continue
            if student.name_student in dates[date]:
                print("студент не должен повторяться")
            dates[date].append(student.name_student)

    # Сортировка и форматирование дат
    dates = dict(sorted(dates.items(), key=lambda item: item[0]))
    dates = {date.isoformat(): old_value for date, old_value in dates.items()}
    student_names = [i.name_student for i in students]
    download_url = url_for(
        'route_to_create_group_students_attendance_download', group_id=group_id, **request.args)
    return render_template(
        "group_attendance_report.html",
        group=group,
        dates=dates,
        student_names=student_names,
        download_url=download_url)


@app.route("/reports/group/<int:group_id>/attendance/students/download")
def route_to_create_group_students_attendance_download(group_id: int):
    """route для отчета успеваемости учеников группы."""
    start_month_str = request.args.get("start_date")  # придет "2025-09"
    end_month_str = request.args.get("end_date")  # придет "2026-01"

    start_date = None
    end_date = None

    if start_month_str:
        # Конвертируем в 1-е число указанного месяца
        start_date = datetime.strptime(start_month_str, "%Y-%m").date()

    if end_month_str:
        # Находим последний день указанного месяца
        temp_date = datetime.strptime(end_month_str, "%Y-%m").date()
        last_day = calendar.monthrange(temp_date.year, temp_date.month)[1]
        end_date = temp_date.replace(day=last_day)
    if start_date and end_date:
        if start_date >= end_date:
            flash("Дата начала не может быть позже даты конца.", "error")
            return redirect(request.referrer or "/")
    ses = create_session()
    group = ses.get(Group, group_id)
    students = group.students
    schedules = group.schedules

    past_schedules: list[PastSchedule] = []
    for schedule in schedules:
        past_schedules += ses.query(PastSchedule).filter_by(
            schedule_id=schedule.id).all()
    dates: dict[str, list[str]] = {}
    for past_schedule in past_schedules:
        date = past_schedule.date
        dates[date] = []
        for student in past_schedule.students:
            student_to_past_schedule = (
                ses.query(Student_to_past_schedule)
                .filter_by(past_schedule_id=past_schedule.id, student_id=student.id)
                .first()
            )
            if not student_to_past_schedule.were_present or student not in students:
                continue
            if student.name_student in dates[date]:
                print("студент не должен повторяться")
            student: Student
            dates[date].append(student.name_student)
    dates = dict(sorted(dates.items(), key=lambda item: item[0]))
    dates = {date.isoformat(): old_value for date, old_value in dates.items()}
    student_names = [i.name_student for i in students]
    excel_file = create_attendance_report_group(
        students_names=student_names, attendance_dict=dates)
    return send_file(
        excel_file,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="attendance_report.xlsx",

    )


@app.route("/reports/teacher_contests")
def teacher_contests_report():
    """Отчет по конкурсам преподавателей"""

    from data.teacher_in_contests import Teacher_in_Contests
    from data import db_session
    import io
    import pandas as pd
    from flask import send_file

    db_sess = db_session.create_session()

    teacher_contests = db_sess.query(Teacher_in_Contests).all()

    data = []
    for tc in teacher_contests:
        teacher = tc.name_teacher
        contest = tc.name_contest

        teacher_name = f"{teacher.surename} {teacher.name}" if teacher else "—"
        contest_name = contest.name if contest else "—"
        place = tc.place if tc.place else "—"
        rank = tc.rank if tc.rank else "—"

        data.append([teacher_name, contest_name, place, rank])

    if not data:
        data = [["Нет данных", "Нет данных", "Нет данных", "Нет данных"]]

    df = pd.DataFrame(
        data, columns=["Преподаватель", "Конкурс", "Место", "Результат"])

    output = io.BytesIO()

    # Используем xlsxwriter (как в ваших работающих отчетах)
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Конкурсы", index=False)
    writer.close()
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="teacher_contests_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/reports/qualifications")
def qualification_report():
    """Отчет по курсам повышения квалификации"""

    from data.teacher_qualification import TeacherQualification
    from data import db_session
    import io
    import pandas as pd
    from flask import send_file
    from datetime import datetime

    db_sess = db_session.create_session()
    qualifications = db_sess.query(TeacherQualification).all()

    data = []
    for q in qualifications:
        teacher = q.teacher
        course = q.course

        # Форматируем ФИО учителя
        if teacher:
            if teacher.patronymic:
                teacher_name = f"{teacher.surename} {teacher.name[0]}.{teacher.patronymic[0]}."
            else:
                teacher_name = f"{teacher.surename} {teacher.name[0]}."
        else:
            teacher_name = "—"

        # Данные из курса
        program_name = course.program_name if course else "—"
        hours = course.hours if course else "—"
        course_organization = course.organization if course else "—"

        # Данные из связующей таблицы
        reg_number = q.registration_number if q.registration_number else "—"
        issue_date = q.issue_date.strftime("%d.%m.%Y") if q.issue_date else "—"
        certificate_number = q.certificate_number if q.certificate_number else "—"
        link = q.link if q.link else "—"

        data.append(
            [teacher_name, program_name, course_organization, hours,
                reg_number, certificate_number, issue_date, link]
        )

    if not data:
        data = [["Нет данных", "—", "—", "—", "—", "—", "—", "—"]]

    df = pd.DataFrame(
        data,
        columns=[
            "Преподаватель",
            "Курс",
            "Организация",
            "Часы",
            "Рег. номер",
            "Номер сертификата",
            "Дата выдачи",
            "Ссылка",
        ],
    )

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Квалификация", index=False)

    # Настраиваем ширину колонок
    workbook = writer.book
    worksheet = writer.sheets["Квалификация"]

    worksheet.set_column("A:A", 25)
    worksheet.set_column("B:B", 40)
    worksheet.set_column("C:C", 30)
    worksheet.set_column("D:D", 10)
    worksheet.set_column("E:E", 20)
    worksheet.set_column("F:F", 20)
    worksheet.set_column("G:G", 15)
    worksheet.set_column("H:H", 30)

    writer.close()
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"qualifications_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
