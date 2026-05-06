from flask import Flask
from flask_restful import Api
from api.v1.groups import GroupListResource, GroupResource
from api.v1.schedules import ScheduleResource, ScheduleListResource
from api.v1.teachers import TeacherResource, TeacherListResource

app = Flask(__name__)
api = Api(app)

api.add_resource(GroupListResource, "/api/v1/groups/")
api.add_resource(GroupResource, "/api/v1/groups/<int:group_id>")

api.add_resource(ScheduleListResource, "/api/v1/schedules/")
api.add_resource(ScheduleResource, "/api/v1/schedules/<int:schedule_id>")


api.add_resource(TeacherListResource, "/api/v1/teachers/")
api.add_resource(TeacherResource, "/api/v1/teachers/<int:teacher_id>")

# api.add_resource(, '/api/v1/')
