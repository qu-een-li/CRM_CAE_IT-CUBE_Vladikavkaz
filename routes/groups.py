from app import app
from flask import render_template, request
from data.db_session import create_session
from data.group import Group


@app.route('/direction/<int:direction_id>/groups')
def show_groups_from_direction(direction_id: int):
    matrix = [[]]
