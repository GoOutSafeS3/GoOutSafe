from monolith.database import User, db, Restaurant, Booking, Notification
from datetime import datetime, timedelta


def mark_as_positive(user_id):
    """ Given an id it marks that user as positive also assigning the timestamp of the current time 
        
        Return:
        True -> The procedure was successful
        False -> otherwise
    """
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
            return False


def unmark_as_positive(user_id):
    """ Given an id it marks that user as negative also deleting the timestamp 
        
        Return:
        True -> The procedure was successful
        False -> otherwise
    """
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
            return False


def get_user_contacts(user_id, date_begin, date_end):
    """ Returns a list of users to which a specified user has come in contact with

    This function returns the list of users that the user specified by user_id
    has come into contact in the period from date_begin to date_end.

    A user is considered to have come in contact with another user if they both
    share a booking at the same restaurant in an overlapping time slice.

    user_id -- The id of the user whose contacts should be returned
    date_begin, date_end -- The time interval in which the contacts have happened
    """

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
    """ Returns the list of restaurants visited by a user in a certain timespan

    A restaurant is considered visited by a user if said user has at least one
    booking for that restaurant in the specified timespan.

    user_id -- The id of the user whose visited restaurants should be returned
    date_begin, date_end -- The timespan in which the restaurants have been visited
    """

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


