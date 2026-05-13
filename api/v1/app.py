from flask import Flask
from flask_restful import Api
from api.v1.groups import GroupListResource, GroupResource
from api.v1.schedules import ScheduleResource, ScheduleListResource
from api.v1.teachers import TeacherResource, TeacherListResource
from api.v1.students import (
    StudentResource,
    StudentListResource,
    StudentInGroupResource,
    StudentsInGroupListResource,
    StudentsInGroupListResource,
)
from api.v1.direction import DirectionListResource, DirectionResource
from api.v1.past_schedules import (
    PastScheduleResource,
    PastScheduleListResource,
    StudentsInPastScheduleResource,
    StudentInPastScheduleResource,
    PastScheduleFromScheduleAndDateResource,
)

app = Flask(__name__)
api = Api(app)

api.add_resource(GroupListResource, "/api/v1/groups/")
api.add_resource(GroupResource, "/api/v1/groups/<int:group_id>")

api.add_resource(ScheduleListResource, "/api/v1/schedules/")
api.add_resource(ScheduleResource, "/api/v1/schedules/<int:schedule_id>")

api.add_resource(PastScheduleListResource, "/api/v1/past_schedules/")
api.add_resource(PastScheduleResource, "/api/v1/past_schedules/<int:past_schedule_id>")

api.add_resource(StudentsInPastScheduleResource, "/api/v1/past_schedules/<int:past_schedule_id>/students")
api.add_resource(
    StudentInPastScheduleResource, "/api/v1/past_schedules/<int:past_schedule_id>/students/<int:student_id>"
)

api.add_resource(
    PastScheduleFromScheduleAndDateResource, "/api/v1/past_schedules/schedule/<int:schedule_id>/date/<date_str>"
)


api.add_resource(TeacherListResource, "/api/v1/teachers/")
api.add_resource(TeacherResource, "/api/v1/teachers/<int:teacher_id>")


api.add_resource(StudentListResource, "/api/v1/students/")
api.add_resource(StudentResource, "/api/v1/students/<int:student_id>")

api.add_resource(StudentInGroupResource, "/api/v1/groups/<int:group_id>/<int:student_id>")
api.add_resource(StudentsInGroupListResource, "/api/v1/groups/<int:group_id>/students")

api.add_resource(DirectionListResource, "/api/v1/directions/")
api.add_resource(DirectionResource, "/api/v1/directions/<int:direction_id>")
# api.add_resource(, '/api/v1/')
