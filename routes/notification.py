from app import app, send_notification_count
from flask import request
from data.notification import Notification
from data.db_session import create_session
from data.user import User


@app.route('/send_notification/<int:user_id>', methods=['POST'])
def send_notification(user_id: int):
    json = request.get_json()
    default_message = 'Ошибка в уведомлении. Просим обратиться к подержке, чтобы помочь в ее исправлении.'
    body = json.get('body', default_message)
    # title = json.get('title', default_message)
    ses = create_session()
    notif = Notification()
    # notif.title = title
    notif.body = body
    notif.user_id = user_id
    ses.add(notif)
    ses.commit()
    send_notification_count(user_id=user_id)
    return 'Уведомление было отправлено.', 200


def send_notification_no_json(user_id: int, body=''):
    ses = create_session()
    notif = Notification()
    # notif.title = title
    notif.body = body
    notif.user_id = user_id
    ses.add(notif)
    ses.commit()
    send_notification_count(user_id=user_id)
    return 'Уведомление было отправлено.', 200


@app.route('/read/all/<int:user_id>', methods=['POST'])
def read_all(user_id: int):
    ses = create_session()
    notifications = ses.query(Notification).filter_by(user_id=user_id).all()
    for notif in notifications:
        notif.is_read = True
    ses.commit()
    return 'OK', 200


@app.route('/delete/notification/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id: int):
    ses = create_session()
    notifications = ses.query(Notification).filter_by(id=notification_id).all()
    for notif in notifications:
        ses.delete(notif)
        break
    ses.commit()
    return 'OK', 200
