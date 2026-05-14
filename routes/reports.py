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
from flask import send_file, request, flash, redirect
from datetime import datetime
import calendar
from babel.dates import format_date


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
    df.columns = ["ФИО обучающегося", "Суммарно количество", "Суммарно", "% пропущенных"]
    # Добавляем индекс (№ п/п)
    df.index = range(1, len(df) + 1)
    df.index.name = "№ п/п"
    df = df.reset_index()

    # Начинаем запись в Excel
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    workbook = writer.book
    worksheet = workbook.add_worksheet("Посещаемость")

    # Настройки форматов
    header_format = workbook.add_format({"bold": True, "align": "center", "valign": "vcenter", "font_size": 14})
    table_header_format = workbook.add_format({"border": 1, "align": "center", "valign": "vcenter", "text_wrap": True})
    cell_format = workbook.add_format({"border": 1, "align": "left", "valign": "vcenter"})
    num_format = workbook.add_format({"border": 1, "align": "right", "valign": "vcenter"})

    worksheet.merge_range("B1:F1", "Сводная ведомость учета посещаемости", header_format)

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

    percent_fmt = workbook.add_format({"border": 1, "num_format": "0%", "align": "right"})
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
    worksheet.write(footer_row + 1, 2, "Процент пропущенных занятий составляет:")
    srednaya_percent /= len(students_data)
    worksheet.write(footer_row + 1, 3, str(int((srednaya_percent) * 100)))

    writer.close()
    output.seek(0)
    print(f"Файл {output} успешно создан!")
    return output


@app.route("/reports/teacher/<int:teacher_id>/attendance/students")
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
        formatted_teacher_name = f"{teacher.surename} {teacher.name[0]}.{teacher.patronymic[0]}.".title()
    else:
        formatted_teacher_name = f"{teacher.surename} {teacher.name[0]}.".title()
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
            courses = ", ".join([direction.name for direction in directions[:-1]])
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
        courses,
        format_date(start_date, format="MMM y", locale="ru_RU") if start_date else "♾️",
        format_date(end_date, format="MMM y", locale="ru_RU") if end_date else "♾️",
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
        df[date] = df.index.map(lambda name: "V" if name in attended_students else "X")

    df.sort_index(inplace=True)

    output = io.BytesIO()

    # Используем xlsxwriter для кастомизации
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Посещаемость")

        workbook = writer.book
        worksheet = writer.sheets["Посещаемость"]

        # 1. Определяем форматы (цвета и стили)
        format_v = workbook.add_format(
            {"bg_color": "#C6EFCE", "font_color": "#006100", "align": "center", "border": 1}
        )  # Светло-зеленый
        format_x = workbook.add_format(
            {"bg_color": "#FFC7CE", "font_color": "#9C0006", "align": "center", "border": 1}
        )  # Розовый
        format_header = workbook.add_format(
            {"bold": True, "bg_color": "#4F81BD", "font_color": "white", "border": 1, "align": "center"}
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
            1, 1, rows, cols, {"type": "cell", "criteria": "equal to", "value": '"V"', "format": format_v}
        )

        worksheet.conditional_format(
            1, 1, rows, cols, {"type": "cell", "criteria": "equal to", "value": '"X"', "format": format_x}
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
        past_schedules += ses.query(PastSchedule).filter_by(schedule_id=schedule.id).all()
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
    excel_file = create_attendance_report_group(students_names=student_names, attendance_dict=dates)
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

    df = pd.DataFrame(data, columns=["Преподаватель", "Конкурс", "Место", "Результат"])

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
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )