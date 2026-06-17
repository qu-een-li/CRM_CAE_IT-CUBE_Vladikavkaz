from flask import Flask, render_template, request, redirect
from config import KEY_CSRF
from data import db_session
from data.student import Student
from flask_login import LoginManager
from api.api_regions import regions_api
from api.api_cities import cities_api
from api.api_schools import schools_api
from data.user import User
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user
from flask_socketio import join_room, SocketIO
from data.notification import Notification

app = Flask(__name__)
app.config["SECRET_KEY"] = KEY_CSRF
app.config["WTF_I18N_ENABLED"] = True
app.config["BABEL_DEFAULT_LOCALE"] = "ru"
# csrf = CSRFProtect(app)
app.register_blueprint(regions_api)
app.register_blueprint(cities_api)
app.register_blueprint(schools_api)

login_manager = LoginManager()
login_manager.init_app(app)


@app.before_request
def check_login():
    if not current_user.is_authenticated and request.endpoint not in ["login", "static"] and not request.path.startswith('/send_notification'):
        return redirect("/login")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove_session()


socketio = SocketIO(app, cors_allowed_origins="*",
                    logger=True, engineio_logger=True)


@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        # Пользователь заходит в свою комнату
        join_room(f"user_{current_user.id}")
        send_notification_count(current_user.id)
    else:
        return False


def send_notification_count(user_id):

    ses = db_session.create_session()
    notifications_all = ses.query(
        Notification).filter_by(user_id=user_id).all()
    notifications = [i for i in notifications_all if i.is_read == False]
    unread_count = len(notifications)

    notif_list = []
    for n in notifications:
        notif_list.append({
            'id': n.id,
            'message': n.body
        })

    socketio.emit('update_badge', {
        'count': unread_count,
        'notifications': notif_list
    }, room=f"user_{user_id}")
