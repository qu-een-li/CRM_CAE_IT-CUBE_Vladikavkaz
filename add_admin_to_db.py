

from data.db_session import create_session, global_init
from data.user import User, UserRole

global_init("db/reg_form.db")

db_sess = create_session()

# Проверяем, нет ли уже админа, чтобы не было ошибки Unique Constraint
admin = User(
    id=1,
    role=UserRole.ADMIN,  # Обращаемся напрямую к элементу Enum
    user_name='admin'
)
admin.set_password('admin')  # Теперь это запишет хеш в колонку password

db_sess.add(admin)
db_sess.commit()
