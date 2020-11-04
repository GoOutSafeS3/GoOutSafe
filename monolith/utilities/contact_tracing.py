from monolith.database import User, db, Restaurant, Booking, Notification
from datetime import datetime, timedelta


def mark_as_positive(user_id):
    try:
        qry = db.session.query(User).filter_by(id = user_id).first()
        if qry is None:
            return False
        else:
            qry.is_positive = True
            qry.positive_datetime = datetime.now()
            db.session.commit()
            return True
    except:
            db.session.rollback()


def unmark_as_positive(user_id):
    try:
        qry = db.session.query(User).filter_by(id = user_id).first()
        if qry is None:
            return False
        else:
            qry.is_positive = False
            qry.positive_datetime = None
            db.session.commit()
            return True
    except:
            db.session.rollback()


def get_user_contacts(user_id, date_begin, date_end):
    user_bookings = db.session.query(Booking).\
        filter(Booking.user_id == user_id).\
        filter(Booking.booking_datetime is not None).\
        filter(Booking.entrance_datetime >= date_begin).\
        filter(Booking.entrance_datetime <= date_end).\
        all()
    user_ids = set()
    for booking in user_bookings:
        interval = timedelta(hours=booking.restaurant.occupation_time)
        a = booking.entrance_datetime + interval
        b = booking.entrance_datetime - interval
        contact_bookings = db.session.query(Booking).\
            filter(Booking.user_id != user_id).\
            filter(Booking.rest_id == booking.rest_id).\
            filter(Booking.entrance_datetime is not None).\
            filter(Booking.entrance_datetime <= a).\
            filter(Booking.entrance_datetime >= b).all()
        for contact in contact_bookings:
            user_ids.add(contact.user_id)
    return db.session.query(User).filter(User.id.in_(list(user_ids))).all()


def get_user_visited_restaurants(user_id, date_begin, date_end):
    restaurants = db.session.query(Restaurant).\
        join(Booking, Booking.rest_id == Restaurant.id).\
        filter(Booking.user_id == user_id).\
        filter(Booking.booking_datetime is not None).\
        filter(Booking.entrance_datetime >= date_begin).\
        filter(Booking.entrance_datetime <= date_end).\
        all()
    return restaurants


def get_operators_contacts(user_id, date_begin, date_end):
    restaurants = get_user_visited_restaurants(user_id,date_begin,date_end)
    operators_ids = set()
    for restaurant in restaurants:
        operator = User.query.filter_by(rest_id=restaurant.id).first()
        operators_ids.add(operator.id)
    return db.session.query(User).filter(User.id.in_(list(operators_ids))).all()


