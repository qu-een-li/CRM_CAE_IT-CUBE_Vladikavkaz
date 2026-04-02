from data.db_session import create_session, global_init
from data.teacher import Teacher
from data.group import Group
from data.schedule import Schedule
global_init("db/reg_form.db")

db_sess = create_session()
md = Teacher()
md.name = 'Имя'
md.surename = 'Фамилия'
md.patronymic = 'Отчество'
db_sess.add(md)

group = Group()
group.name_of_group = 'Название группы'
group.teacher_id = 1
# group.study_period_id = 1
db_sess.add(group)

db_sess.commit()
