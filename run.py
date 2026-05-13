from app import app
from data import db_session
from routes import (
    main,
    students,
    search,
    schedule,
    attendance,
    teachers,
    contests,
    groups,
    error_handlers,
    user,
    teachers_contests,
    reports,
    qualification_courses,
    teachers_qualifications,
    teachers_in_contests
)
import os
from config import UPLOAD_FOLDER, PORT, HOST
import locale

locales = ["ru_RU.UTF-8", "ru_RU", "Russian_Russia.65001", "Russian"]

# обратная совместимость локали и с linux и c windows
for loc in locales:
    try:
        locale.setlocale(locale.LC_TIME, loc)
        break
    except locale.Error:
        continue


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db_session.global_init("db/reg_form.db")
if __name__ == "__main__":
    app.run(port=PORT, host=HOST, debug=True)
