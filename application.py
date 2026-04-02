from flask import Flask
from config import KEY_CSRF
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = KEY_CSRF

login_manager = LoginManager()
