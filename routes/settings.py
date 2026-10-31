from app import app
from flask import render_template, request, redirect, flash, abort
from flask_login import current_user
from data.db_session import create_session
from data.base_values import load_base_values, save_base_values
from data.direction import Direction
from data.auditorium import Auditorium
from data.group import Group
from data.schedule import Schedule
from data.user import UserRole

SECTIONS = ("group_types", "directions", "auditoriums")


def admin_only():
    if getattr(current_user, "role", None) != UserRole.ADMIN:
        abort(403)


def item_name(section, item):
    """Название элемента базовых значений (у типов групп — подпись, у направлений — имя, аудитории — строка)"""
    if section == "group_types":
        return item["title"]
    if section == "directions":
        return item["name"]
    return item


@app.route("/settings")
def settings():
    """Настройки сайта: базовые значения центра из base_values.json"""
    admin_only()
    values = load_base_values()
    session = create_session()

    db_directions = {d.name: d for d in session.query(Direction).all()}
    db_auditoriums = {a.name: a for a in session.query(Auditorium).all()}
    groups = session.query(Group).all()
    groups_by_type = {}
    for g in groups:
        groups_by_type[g.group_type] = groups_by_type.get(g.group_type, 0) + 1

    base_direction_names = {d["name"] for d in values["directions"]}
    return render_template(
        "settings.html",
        values=values,
        db_directions=db_directions,
        db_auditoriums=db_auditoriums,
        groups_by_type=groups_by_type,
        # есть в текущей базе, но нет в базовых значениях — можно перенести в base_values.json
        extra_directions=[d for name, d in db_directions.items() if name not in base_direction_names],
        extra_auditoriums=[a for name, a in db_auditoriums.items() if name not in values["auditoriums"]],
    )


@app.route("/settings/<section>/add", methods=["POST"])
def settings_add(section):
    """Добавление базового значения: пишется в base_values.json и сразу добавляется в текущую базу"""
    admin_only()
    if section not in SECTIONS:
        abort(404)
    values = load_base_values()
    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Введите название", "warning")
        return redirect(f"/settings#{section}")
    if any(item_name(section, item).lower() == name.lower() for item in values[section]):
        flash(f"«{name}» уже есть в списке", "warning")
        return redirect(f"/settings#{section}")

    session = create_session()
    if section == "group_types":
        value = name.lower()
        if any(t["value"] == value for t in values[section]):
            flash(f"Тип «{name}» уже есть в списке", "warning")
            return redirect(f"/settings#{section}")
        values[section].append({"value": value, "title": name, "weekly": bool(request.form.get("weekly"))})
    elif section == "directions":
        icon = (request.form.get("icon") or "").strip() or "bi-code-slash"
        values[section].append({"name": name, "icon": icon})
        if not session.query(Direction).filter(Direction.name == name).first():
            session.add(Direction(name=name, icon_bootstrap=icon))
    else:
        values[section].append(name)
        if not session.query(Auditorium).filter(Auditorium.name == name).first():
            session.add(Auditorium(name=name))

    save_base_values(values)
    session.commit()
    flash(f"«{name}» добавлено", "success")
    return redirect(f"/settings#{section}")


@app.route("/settings/<section>/delete", methods=["POST"])
def settings_delete(section):
    """Удаление базового значения из base_values.json.
    Из текущей базы направление/аудитория удаляются, только если ими ещё никто не пользуется."""
    admin_only()
    if section not in SECTIONS:
        abort(404)
    values = load_base_values()
    name = request.form.get("name") or ""
    items = [item for item in values[section] if item_name(section, item) == name]
    if not items:
        flash("Такого значения уже нет", "warning")
        return redirect(f"/settings#{section}")
    values[section] = [item for item in values[section] if item_name(section, item) != name]

    session = create_session()
    message = f"«{name}» удалено из базовых значений"
    if section == "group_types":
        used = session.query(Group).filter(Group.group_type == items[0]["value"]).count()
        if used:
            message += f". У {used} уже созданных групп тип останется, но выбрать его для новой группы будет нельзя"
    elif section == "directions":
        direction = session.query(Direction).filter(Direction.name == name).first()
        if direction:
            used = session.query(Group).filter(Group.direction_id == direction.id).count()
            if used:
                message += f". В текущей базе направление осталось — в нём {used} групп(ы)"
            else:
                session.delete(direction)
    else:
        auditorium = session.query(Auditorium).filter(Auditorium.name == name).first()
        if auditorium:
            used = session.query(Schedule).filter(Schedule.auditorium_id == auditorium.id).count() + \
                session.query(Group).filter(Group.auditorium_id == auditorium.id).count()
            if used:
                message += f". В текущей базе аудитория осталась — в ней есть занятия ({used})"
            else:
                session.delete(auditorium)

    save_base_values(values)
    session.commit()
    flash(message, "success")
    return redirect(f"/settings#{section}")


@app.route("/settings/group_types/weekly", methods=["POST"])
def settings_group_type_weekly():
    """Переключение «занятия каждую неделю» у типа группы"""
    admin_only()
    values = load_base_values()
    value = request.form.get("value")
    for t in values["group_types"]:
        if t["value"] == value:
            t["weekly"] = not t.get("weekly", False)
    save_base_values(values)
    return redirect("/settings#group_types")
