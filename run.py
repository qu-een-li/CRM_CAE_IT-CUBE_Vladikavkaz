from app import app
from data import db_session
from routes import main, students, search, schedule, attendance, teachers, contests, groups, error_handlers, user, teachers_contests
import os
from config import UPLOAD_FOLDER, PORT, HOST
import locale

locale.setlocale(locale.LC_TIME, "Russian_Russia.65001")

if __name__ == "__main__":

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    db_session.global_init("db/reg_form.db")
    app.run(
        port=PORT,
        host=HOST,
        debug=True,
    )
