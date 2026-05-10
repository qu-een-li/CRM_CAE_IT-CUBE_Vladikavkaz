from flask_restful import Resource, abort
from flask import request
from data.direction import Direction
from data import db_session
import datetime

from api.api_base import require_api_key


class DirectionListResource(Resource):
    # Применит декоратор ко всем методам класса
    method_decorators = [require_api_key]

    def get(self):
        fields = request.args.getlist('fields')
        add_fields = request.args.getlist('add_fields')
        session = db_session.create_session()
        try:
            directions = session.query(Direction).all()
            if not directions:
                abort(404, message="Directions not found")
            ans = []
            for item in directions:
                direction_dict = item.to_dict(*fields)
                if 'groups' in add_fields:
                    direction_dict['groups'] = [group.to_dict()
                                                for group in item.groups]
                ans.append(direction_dict)
            return ans
        finally:
            session.close()

    def post(self):

        data = request.get_json()
        session = db_session.create_session()

        try:
            # 1. Получаем список всех имен колонок нашей модели
            # Это 'id', 'group_id', 'date', 'start_time' и т.д.
            allowed_columns = {
                column.name: column for column in Direction.__table__.columns}
            filtered_data = {}
            for column_name, value in data.items():
                if isinstance(value, str):
                    try:
                        column = allowed_columns[column_name]
                        python_type = column.type.python_type

                        if python_type is datetime.date:
                            value = datetime.date.fromisoformat(value)
                        elif python_type is datetime.time:
                            value = datetime.time.fromisoformat(value)
                        elif python_type is datetime.datetime:
                            value = datetime.datetime.fromisoformat(value)
                    except (ValueError, TypeError):
                        abort(400)
                if column_name in allowed_columns:
                    filtered_data[column_name] = value
                else:
                    abort(400)
            new_direction = Direction(**filtered_data)

            session.add(new_direction)
            session.commit()
            return new_direction.to_dict(), 201

        except Exception as e:
            session.rollback()
            abort(400, message=str(e))
        finally:
            session.close()


class DirectionResource(Resource):
    method_decorators = [require_api_key]

    def get(self, direction_id: int):
        fields = request.args.getlist('fields')
        add_fields = request.args.getlist('add_fields')
        # поля дря прогрузки mtm свзяей
        session = db_session.create_session()
        try:
            direction = session.query(Direction).get(direction_id)
            possibly_add_fields = {'groups': direction.groups}
            if not direction:
                abort(404, message=f"Direction {direction_id} not found")
            ans = direction.to_dict(*fields)
            for add_field_name in add_fields:
                if add_field_name in possibly_add_fields:
                    ans[add_field_name] = [group.to_dict()
                                           for group in possibly_add_fields[add_field_name]]
            return ans
        finally:
            session.close()
