from flask import Flask, render_template, request, redirect
from config import KEY_CSRF
from data import db_session
from data.student import Student
from flask_login import LoginManager
from api.api_regions import regions_api
from api.api_cities import cities_api
from api.api_schools import schools_api


app = Flask(__name__)
app.config["SECRET_KEY"] = KEY_CSRF

app.register_blueprint(regions_api)
app.register_blueprint(cities_api)
app.register_blueprint(schools_api)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Student).get(user_id)
