from flask_restful import Resource, abort
from flask import request, jsonify
from data.student import Student
from data.group import Group
from data import db_session
from data.direction import Direction
import datetime

from api.api_base import require_api_key


class StudentListResource(Resource):
    # Применит декоратор ко всем методам класса
    method_decorators = [require_api_key]

    def get(self):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            students = session.query(Student).all()
            if not students:
                abort(404, message="Groups not found")
            return [item.to_dict(*fields) for item in students]
        finally:
            session.close()

    def post(self):
        data = request.get_json()
        session = db_session.create_session()

        try:
            # 1. Получаем список всех имен колонок нашей модели
            # Это 'id', 'group_id', 'date', 'start_time' и т.д.
            allowed_columns = {
                column.name: column for column in Student.__table__.columns}
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
            new_student = Student(**filtered_data)

            session.add(new_student)
            session.commit()
            return new_student.to_dict(), 201

        except Exception as e:
            session.rollback()
            abort(400, message=str(e))
        finally:
            session.close()


class StudentResource(Resource):
    method_decorators = [require_api_key]

    def get(self, student_id: int):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            student = session.query(Student).get(student_id)
            if not student:
                abort(404, message=f"Student {student_id} not found")
            return student.to_dict(*fields)
        finally:
            session.close()


class StudentInGroupResource(Resource):
    # method_decorators = [require_api_key]
    cors_headers = {'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, DELETE, OPTIONS, PUT',
                    'Access-Control-Allow-Headers': 'Content-Type, X-CSRFToken',
                    'Access-Control-Allow-Credentials': 'true'
                    }

    def options(self, group_id, student_id):
        # Ручной ответ на preflight запрос
        return {'Allow': 'POST'}, 200, \
            self.cors_headers

    def delete(self, group_id, student_id):
        sess = db_session.create_session()
        group = sess.get(Group, group_id)
        student = sess.get(Student, student_id)

        # 2. Проверяем, что оба объекта существуют
        if not group or not student:
            abort(404, message="Группа или студент не найдены")

        try:
            # 3. Удаляем связь (предполагается, что в модели Group есть relationship 'students')
            if student in group.students:
                group.students.remove(student)
                sess.commit()
                return None, 204, self.cors_headers  # Успех, без тела ответа
            else:
                abort(400, message="Студент не состоит в этой группе")

        except Exception as e:
            sess.rollback()  # Откатываем в случае ошибки
            abort(500, message=str(e))
        finally:
            sess.close()

    def post(self, group_id, student_id):
        sess = db_session.create_session()
        group = sess.get(Group, group_id)
        student = sess.get(Student, student_id)

        # 2. Проверяем, что оба объекта существуют
        if not group or not student:
            abort(404, message="Группа или студент не найдены")

        try:
            # 3. Удаляем связь (предполагается, что в модели Group есть relationship 'students')
            if student not in group.students:
                group.students.append(student)
                sess.commit()
                return None, 204  # Успех, без тела ответа
            else:
                abort(400, message="Студент итак состоит в этой группе")

        except Exception as e:
            sess.rollback()  # Откатываем в случае ошибки
            abort(500, message=str(e))
        finally:
            sess.close()

    def put(self, group_id, student_id):
        sess = db_session.create_session()
        group = sess.get(Group, group_id)
        student = sess.get(Student, student_id)

        # 2. Проверяем, что оба объекта существуют
        if not group or not student:
            abort(404, message="Группа или студент не найдены")

        try:
            # 3. Удаляем связь (предполагается, что в модели Group есть relationship 'students')
            direction: Direction = group.direction
            was_student_in_the_direction = False
            for group1 in direction.groups:
                group1: Group
                if student in group1.students:
                    # Удаляем студента из всех групп направления
                    # куда мы его кидам (на крайний случай, если он вдру как-то попал в несколько)
                    group1.students.remove(student)
                    was_student_in_the_direction = True
            if not was_student_in_the_direction:
                abort(
                    400, message=f"Студент не состоит не в одной группе направления {direction.name}")
            if student not in group.students:
                group.students.append(student)
                sess.commit()
                return None, 204, self.cors_headers  # Успех, без тела ответа
            else:
                abort(400, message="Студент итак состоит в этой группе")

        except Exception as e:
            sess.rollback()  # Откатываем в случае ошибки
            abort(500, message=str(e))
        finally:
            sess.close()


class StudentsInGroupListResource(Resource):
    def get(self, group_id):
        fields = request.args.getlist('fields')
        session = db_session.create_session()
        try:
            group = session.query(Group).get(group_id)
            students = group.students
            if not students:
                abort(404, message="Students not found")
            return [item.to_dict(*fields) for item in students]
        finally:
            session.close()
