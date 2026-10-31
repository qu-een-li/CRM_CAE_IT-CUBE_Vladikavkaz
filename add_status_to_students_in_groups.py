import sqlite3


conn = sqlite3.connect('db/reg_form.db')
cursor = conn.cursor()

# статус ученика в группе: 0 - ученик, 1 - кандидат (см. data/student_in_group.py)
try:
    cursor.execute('ALTER TABLE students_in_groups ADD COLUMN status INTEGER NOT NULL DEFAULT 0')
    print("столбец status добавлен")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("столбец status уже есть")
    else:
        print(f"ошибка: {e}")

# защита от двойного добавления одного ученика в одну и ту же группу
# (в разные группы добавлять можно)
try:
    cursor.execute('''
        DELETE FROM students_in_groups
        WHERE rowid NOT IN (SELECT MIN(rowid) FROM students_in_groups GROUP BY group_id, student_id)
    ''')
    print(f"удалено дублей: {cursor.rowcount}")
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS ux_students_in_groups_group_student
        ON students_in_groups (group_id, student_id)
    ''')
    print("уникальный индекс (group_id, student_id) создан")
except sqlite3.OperationalError as e:
    print(f"ошибка: {e}")

conn.commit()
conn.close()
