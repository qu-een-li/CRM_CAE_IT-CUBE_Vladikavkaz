from app import app
from flask import render_template
from data.group import Group
from data.direction import Direction
from data.db_session import create_session
from data.schedule import FrequencyType
from data.base_values import group_type_title

WEEKDAYS_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


def schedule_label(group):
    """Короткая подпись расписания группы для карточки на главной: 'Пн 15:00–16:30' или '12.11 15:00–16:30'"""
    lessons = [s for s in group.schedules if not s.is_cancelled]
    if not lessons:
        return None
    labels = []
    for s in sorted(lessons, key=lambda s: (s.date, s.start_time)):
        times = f"{s.start_time:%H:%M}–{s.end_time:%H:%M}"
        if s.frequency == FrequencyType.WEEK:
            label = f"{WEEKDAYS_SHORT[s.date.weekday()]} {times}"
        else:
            label = f"{s.date:%d.%m} {times}"
        if label not in labels:
            labels.append(label)
    return ", ".join(labels[:2]) + (" …" if len(labels) > 2 else "")


@app.route('/')
def index():
    ses = create_session()

    directions_raw = ses.query(Direction).all()
    directions = {}
    for direction in directions_raw:
        directions[direction.id] = {
            'name': direction.name,
            'icon': direction.icon_bootstrap,
            'groups': [
                {
                    'id': group.id,
                    'title': group.name_of_group,
                    'n_of_students': len(group.students),
                    'tag': group_type_title(group.group_type),
                    'schedule': schedule_label(group),
                } for group in direction.groups
            ]
        }

    return render_template('index.html', directions=directions)
