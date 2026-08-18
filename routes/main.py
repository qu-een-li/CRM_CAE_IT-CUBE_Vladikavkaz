from app import app
from flask import render_template
from data.group import Group
from data.direction import Direction
from data.db_session import create_session


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
                    'tag': group.group_type,
                    'schedule': None,
                } for group in direction.groups
            ]
        }

    return render_template('index.html', directions=directions)
