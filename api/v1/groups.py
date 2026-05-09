from flask_restful import Resource, abort
from data.group import Group
from data import db_session
from api.api_base import require_api_key
from flask import request


class GroupListResource(Resource):
    # Применит декоратор ко всем методам класса
    method_decorators = [require_api_key]

    def get(self):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            groups = session.query(Group).all()
            if not groups:
                abort(404, message="Groups not found")
            return [item.to_dict(*fields) for item in groups]
        finally:
            session.close()


class GroupResource(Resource):
    method_decorators = [require_api_key]

    def get(self, group_id: int):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            group = session.query(Group).get(group_id)
            if not group:
                abort(404, message=f"Group {group_id} not found")
            return group.to_dict(*fields)
        finally:
            session.close()
