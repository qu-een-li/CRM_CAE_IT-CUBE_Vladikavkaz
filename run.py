from app import app
from data import db_session
from routes import main, students, search, schedule
import locale
locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')

if __name__ == '__main__':
    db_session.global_init("db/reg_form.db")
    app.run(port=8080, host='127.0.0.1')
