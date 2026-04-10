from app import app
from flask import render_template, request
from data.db_session import create_session
from data.group import Group
from data.direction import Direction
from itertools import zip_longest


@app.route('/direction/<int:direction_id>/groups')
def show_groups_from_direction(direction_id: int):
    db_sess = create_session()
    direction = db_sess.get(Direction, direction_id)
    groups: list[Group] = direction.groups
    matrix = [[i.name_of_group for i in groups]]
    for row in zip_longest(*[[student.name_student for student in i.students] for i in groups], fillvalue=''):
        matrix.append(list(row))
    return render_template('show_groups_of_direction.html', table_data=matrix, direction_name=direction.name)
