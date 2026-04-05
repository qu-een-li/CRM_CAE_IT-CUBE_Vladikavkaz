from data.db_session import create_session, global_init
from data.teacher import Teacher
from data.group import Group
from data.schedule import Schedule
from datetime import datetime
global_init("db/reg_form.db")

db_sess = create_session()
md = Teacher()
md.name = 'Имя'
md.surename = 'Фамилия'
md.patronymic = 'Отчество'
md.email = ''
md.personal_photos = ''
md.status = ''
md.phone = ''
md.birthday = ''


db_sess.add(md)

group = Group()
group.name_of_group = 'Название группы'
group.teacher_id = 1
group.description = 'описание'
group.level_of_education = 'high'
group.study_period_id = 1
group.duration = datetime.now().time()
# group.study_period_id = 1
db_sess.add(group)

sc = Schedule()
sc.date = datetime.now().date()
sc.group_id = 1
sc.start_time = datetime.now().time()
sc.end_time = datetime.now().time()
db_sess.add(sc)

db_sess.commit()
