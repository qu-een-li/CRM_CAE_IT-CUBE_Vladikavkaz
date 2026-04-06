from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import Session
from data.group import Group
from data.schedule import Schedule
from data.study_period import Study_period


class GroupService:

    @staticmethod
    def auditorium_free(session: Session, auditorium_id: int, date, start_time, end_time):
        query = session.query(Schedule).filter(
            Schedule.auditorium_id == auditorium_id,
            Schedule.date == date,
            Schedule.start_time < end_time,
            Schedule.end_time > start_time,
            Schedule.is_cancelled == False
        )
        return query.count() == 0

    @staticmethod
    def generate_semester_lessons(first_lesson_date: date, start_time: time, end_time: time, add_days: list,
                                  period_start: date, period_end: date) -> list:
        first_day_of_week = first_lesson_date.isoweekday()
        week_days = [first_day_of_week]
        for day in add_days:
            week_days.append(day)
        all_lessons = []

        for day in week_days:
            cur_date = first_lesson_date
            while cur_date.isoweekday() != day:
                cur_date += timedelta(days=1)

            while cur_date <= period_end:
                if cur_date >= period_start:
                    all_lessons.append({"date": cur_date, "start_time": start_time, "end_time": end_time})
                cur_date += timedelta(days=7)

        return sorted(all_lessons, key=lambda x: x["date"])

    @staticmethod
    def create_semester_group(session: Session, name_of_group: str, teacher_id: int, direction_id: int,
                              level_of_group: str, study_period_id: int, auditorium_id: int, first_lesson_date: str,
                              start_time: str, end_time: str, add_days: list, description: str = None) -> Group:

        study_period = session.query(Study_period).filter(Study_period.id == study_period_id).first()

        first_date = datetime.strptime(first_lesson_date, "%Y-%m-%d").date()
        start = datetime.strptime(start_time, "%H:%M").time()
        end = datetime.strptime(end_time, "%H:%M").time()

        lessons = GroupService.generate_semester_lessons(first_lesson_date=first_date, start_time=start, end_time=end,
                                                         add_days=add_days, period_start=study_period.date_start,
                                                         period_end=study_period.date_end)

        for lesson in lessons:
            if not GroupService.auditorium_free(session, auditorium_id, lesson["date"], lesson["start_time"], lesson["end_time"]):
                raise ValueError(f"аудитория занята {lesson['date']} в {lesson['start_time']}")

        group = Group(name_of_group=name_of_group, teacher_id=teacher_id, direction_id=direction_id,
                      group_type="семестровый", level_of_group=level_of_group, study_period_id=study_period_id,
                      auditorium_id=auditorium_id,
                      start_time=start, end_time=end, first_lesson_date=first_date, add_days=add_days,
                      description=description)
        session.add(group)
        session.flush() # для получения id группы и возможности отката

        schedules = []
        for lesson in lessons:
            schedule = Schedule(group_id=group.id, date=lesson["date"], start_time=lesson["start_time"],
                                end_time=lesson["end_time"], auditorium_id=auditorium_id)
            schedules.append(schedule)

        session.bulk_save_objects(schedules) # для быстроты мы отправляем ОДИН запрос
        session.commit()

        return group

    @staticmethod
    def create_intensive_group(session: Session, name_of_group: str, teacher_id: int, direction_id: int,
                               level_of_group: str, study_period_id: int, auditorium_id: int, custom_lessons: list,
                               description: str = None) -> Group:

        study_period = session.query(Study_period).filter(Study_period.id == study_period_id).first()

        for lesson in custom_lessons:
            lesson_date = datetime.strptime(lesson["date"], "%Y-%m-%d").date()
            if lesson_date < study_period.date_start or lesson_date > study_period.date_end:
                raise ValueError(f"дата {lesson['date']} выходит за пределы учебного периода")

        for lesson in custom_lessons:
            lesson_date = datetime.strptime(lesson["date"], "%Y-%m-%d").date()
            lesson_start = datetime.strptime(lesson["start_time"], "%H:%M").time()
            lesson_end = datetime.strptime(lesson["end_time"], "%H:%M").time()

            if not GroupService.auditorium_free(session, auditorium_id, lesson_date, lesson_start, lesson_end):
                raise ValueError(f"аудитория занята {lesson['date']} в {lesson['start_time']}")

        group = Group(name_of_group=name_of_group, teacher_id=teacher_id, direction_id=direction_id, group_type="интенсив",
                level_of_group=level_of_group, study_period_id=study_period_id, auditorium_id=auditorium_id, description=description)
        session.add(group)
        session.flush()

        schedules = []
        for lesson in custom_lessons:
            schedule = Schedule(group_id=group.id, date=datetime.strptime(lesson["date"], "%Y-%m-%d").date(),
                                start_time=datetime.strptime(lesson["start_time"], "%H:%M").time(),
                                end_time=datetime.strptime(lesson["end_time"], "%H:%M").time(), auditorium_id=auditorium_id)
            schedules.append(schedule)

        session.bulk_save_objects(schedules)
        session.commit()

        return group

    @staticmethod
    def create_masterclass_group(session: Session, name_of_group: str, teacher_id: int, direction_id: int, level_of_group: str,
                                study_period_id: int, auditorium_id: int, date: str, start_time: str, end_time: str,
                                 description: str = None) -> Group:

        study_period = session.query(Study_period).filter(Study_period.id == study_period_id).first()
        lesson_date = datetime.strptime(date, '%Y-%m-%d').date()
        lesson_start = datetime.strptime(start_time, '%H:%M').time()
        lesson_end = datetime.strptime(end_time, '%H:%M').time()

        if not GroupService.auditorium_free(session, auditorium_id, lesson_date, lesson_start, lesson_end):
            raise ValueError(f"аудитория занята {date} в {start_time}")

        group = Group(name_of_group=name_of_group, teacher_id=teacher_id, direction_id=direction_id,
                      group_type="мастер-класс", level_of_group=level_of_group, study_period_id=study_period_id,
                      auditorium_id=auditorium_id, start_time=lesson_start, end_time=lesson_end, description=description)
        session.add(group)
        session.flush()

        schedule = Schedule(group_id=group.id, date=lesson_date, start_time=lesson_start, end_time=lesson_end, auditorium_id=auditorium_id)
        session.add(schedule)
        session.commit()

        return group
