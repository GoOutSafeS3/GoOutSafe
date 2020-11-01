import datetime
from datetime import timedelta, datetime
from monolith.database import Notification, db


def add_notification(user_positive_id, user_notified_id):
    if Notification.query.filter_by(user_positive_id=user_positive_id, user_notified_id=user_notified_id).first() is None:
        new_notification = Notification()
        new_notification.user_positive_id = user_positive_id
        new_notification.user_notified_id = user_notified_id
        new_notification.already_read = False
        new_notification.datetime = datetime.today()
        db.session.add(new_notification)
        db.session.commit()
        return True
    return False


def delete_notification(user_positive_id, user_notified_id):
    notification = Notification.query.filter_by(user_positive_id=user_positive_id, user_notified_id=user_notified_id).first()
    if notification is not None:
        notification.already_read = True
        db.session.commit()
        return True
    return False