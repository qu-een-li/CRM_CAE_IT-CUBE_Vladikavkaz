from app import app
from data import db_session
from routes import main, students, search, schedule


if __name__ == '__main__':
    db_session.global_init("db/reg_form.db")
    app.run(port=8080, host='127.0.0.1')
