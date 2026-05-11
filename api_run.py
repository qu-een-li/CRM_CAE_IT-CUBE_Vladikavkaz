from api.v1.app import app
from config import API_HOST, API_PORT
from data import db_session

if __name__ == "__main__":
    db_session.global_init("db/reg_form.db")
    app.run(API_HOST, port=int(API_PORT), debug=True)
