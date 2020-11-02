from monolith.database import db, Restaurant, Booking, Table
from datetime import datetime, timedelta


def is_busy_table(tab_id):
    qr = db.session.query(Restaurant).join(Restaurant.tables, aliased=True).filter(Table.id == tab_id).first()
    occupation_time = qr.occupation_time
    qr = db.session.query(Table).join(Table.bookings, aliased=True).filter(Table.id == tab_id).filter(Booking.booking_datetime >= datetime.now()+timedelta(hours=occupation_time)).first()
    return qr is not None


def validate_hours(opening_lunch, closing_lunch, opening_dinner, closing_dinner):
    """
    :type opening_lunch: Integer
    :type opening_dinner: Integer
    :type closing_dinner: Integer
    :type closing_lunch: Integer
    """
    if opening_lunch > closing_lunch or opening_lunch > opening_dinner or opening_lunch > closing_dinner:
        return False
    if closing_lunch > opening_dinner or closing_lunch > closing_dinner:
        return False
    if opening_dinner > closing_dinner:
        return False
    if closing_dinner > 24 and closing_dinner-24 > opening_lunch: # restaurant may be open after midnight, check that the opening the day after does not conflict with the closing
        return False
    return True