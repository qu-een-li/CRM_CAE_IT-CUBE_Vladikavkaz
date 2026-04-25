import sqlite3


conn = sqlite3.connect('db/reg_form.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE contests ADD COLUMN end_date DATE')
    print("столбц end_date добавлен")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("столбец end_date уже есть")
    else:
        print(f"ошибка: {e}")

conn.commit()
conn.close()