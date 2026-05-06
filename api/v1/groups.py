from flask_restful import Resource, abort
from data.group import Group
from data import db_session
from api.api_base import require_api_key


class GroupListResource(Resource):
    method_decorators = [require_api_key]  # Применит декоратор ко всем методам класса

    def get(self):
        session = db_session.create_session()
        try:
            groups = session.query(Group).all()
            if not groups:
                abort(404, message="Groups not found")
            return [item.to_dict() for item in groups]
        finally:
            session.close()


class GroupResource(Resource):
    method_decorators = [require_api_key]

    def get(self, group_id: int):
        session = db_session.create_session()
        try:
            group = session.query(Group).get(group_id)
            if not group:
                abort(404, message=f"Group {group_id} not found")
            return group.to_dict()
        finally:
            session.close()
