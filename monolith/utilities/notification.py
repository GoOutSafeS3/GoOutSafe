import datetime
from datetime import timedelta, datetime
from monolith.database import Notification, db, Booking, User, Restaurant


def add_notification(user_positive_id, user_notified_id, type):
    if Notification.query.filter_by(user_positive_id=user_positive_id, user_notified_id=user_notified_id).first() is None:
        new_notification = Notification()
        new_notification.user_positive_id = user_positive_id
        new_notification.user_notified_id = user_notified_id
        new_notification.operator_notification_type = type
        new_notification.already_read = False
        new_notification.datetime = datetime.today()
        db.session.add(new_notification)
        db.session.commit()
        return True
    return False


def add_notification_restaurant_closed(rest, user_notified_id, booking_datetime):
    today = datetime.today()
    notification = Notification()
    notification.datetime = today
    notification.user_booking_date = booking_datetime
    notification.already_read = False
    notification.user_notified_id = user_notified_id
    notification.rest_closed_name = rest.name
    notification.customer_notification_type = 1
    db.session.add(notification)
    db.session.commit()


def delete_notification(notification_id):
    notification = Notification.query.filter_by(notification_id=notification_id).first()
    if notification is not None:
        notification.already_read = True
        db.session.commit()
        return True
    return False


def add_bookings_notifications(user_id):
    today = datetime.today()
    user_bookings = db.session.query(Booking). \
        filter(Booking.user_id == user_id). \
        filter(Booking.booking_datetime >= today). \
        all()
    for b in user_bookings:
        notification = Notification()
        notification.datetime = today
        notification.user_positive_id = user_id
        notification.user_booking_date = b.booking_datetime
        user = User.query.filter_by(id=user_id).first()
        if user is not None:
            notification.user_positive_email = user.email
            notification.user_positive_name = user.firstname + " " + user.lastname
            operator = User.query.filter_by(rest_id=b.rest_id).first()
            if operator is not None:
                notification.user_notified_id = operator.id
                notification.operator_notification_type = 2
                search_notification = Notification.query.filter_by(user_positive_id=user_id,
                                                                   user_notified_id=operator.id,
                                                                   user_booking_date=b.booking_datetime,
                                                                   user_positive_email=user.email).first()
                if search_notification is None:
                    db.session.add(notification)
                    db.session.commit()
