"""Базовые значения центра (типы групп, направления, аудитории).

Хранятся в base_values.json в корне проекта: в другом центре там будут свои значения.
Редактируются на странице /settings. При создании новой (пустой) базы данных
направления и аудитории заполняются из этого файла автоматически.
"""
import json
import os

BASE_VALUES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "base_values.json")

# значения по умолчанию — если файла base_values.json нет, он создаётся с ними
DEFAULT_BASE_VALUES = {
    # value — что пишется в groups.group_type, title — как показывается,
    # weekly — первое занятие повторяется каждую неделю (иначе — разовое событие)
    "group_types": [
        {"value": "семестровый", "title": "Полугодовая", "weekly": True},
        {"value": "мастер-класс", "title": "Мастер-класс", "weekly": False},
        {"value": "интенсив", "title": "Интенсив", "weekly": False},
    ],
    # icon — иконка Bootstrap Icons для карточки направления на главной
    "directions": [
        {"name": "Программирование на Python", "icon": "bi-code-slash"},
        {"name": "VR/AR", "icon": "bi-badge-vr"},
        {"name": "Системное администрирование", "icon": "bi-hdd-network"},
        {"name": "Алгоритмика", "icon": "bi-diagram-3"},
        {"name": "Мобильная разработка", "icon": "bi-phone"},
        {"name": "Робототехника", "icon": "bi-cpu"},
    ],
    "auditoriums": [
        "Программирование на Python",
        "VR/AR",
        "Системное администрирование",
        "Алгоритмика",
        "Мобильная разработка",
        "Робототехника",
        "холл",
    ],
}


def load_base_values():
    """Читает base_values.json; если файла нет или он испорчен — берёт значения по умолчанию и создаёт файл"""
    try:
        with open(BASE_VALUES_FILE, encoding="utf-8") as f:
            values = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        values = json.loads(json.dumps(DEFAULT_BASE_VALUES))
        save_base_values(values)
    for key, default in DEFAULT_BASE_VALUES.items():
        values.setdefault(key, list(default))
    return values


def save_base_values(values):
    """Сохраняет base_values.json (сначала во временный файл, чтобы не испортить его при сбое)"""
    tmp_file = BASE_VALUES_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(values, f, ensure_ascii=False, indent=4)
    os.replace(tmp_file, BASE_VALUES_FILE)


def get_group_types():
    return load_base_values()["group_types"]


def group_type_choices():
    """Варианты для выпадающего списка «Тип группы»"""
    return [(t["value"], t["title"]) for t in get_group_types()]


def group_type_title(value):
    """Подпись типа группы; для типа, которого уже нет в настройках, показываем как записано в базе"""
    return next((t["title"] for t in get_group_types() if t["value"] == value), value)


def is_weekly_group_type(value):
    return next((t.get("weekly", False) for t in get_group_types() if t["value"] == value), False)


def seed_database(session):
    """Заполняет пустую базу: направления и аудитории из base_values.json, уровни конкурсов и администратор.
    Таблицы, в которых уже есть записи, не трогаются — удалённое через сайт не появится снова."""
    from data.direction import Direction
    from data.auditorium import Auditorium
    from data.level_contest import Level_contest
    from data.user import User, UserRole

    values = load_base_values()
    if not session.query(Direction).first():
        for d in values["directions"]:
            session.add(Direction(name=d["name"], icon_bootstrap=d.get("icon") or "bi-code-slash"))
        print("Направления добавлены из base_values.json")
    if not session.query(Auditorium).first():
        for name in values["auditoriums"]:
            session.add(Auditorium(name=name))
        print("Аудитории добавлены из base_values.json")
    if not session.query(Level_contest).first():
        Level_contest.init_data(session)
    if not session.query(User).first():
        # как в add_admin_to_db.py — без пользователя в новую базу не войти
        admin = User(role=UserRole.ADMIN, user_name="admin")
        admin.set_password("admin")
        session.add(admin)
        print("Создан пользователь admin с паролем admin — смените пароль!")
    session.commit()
