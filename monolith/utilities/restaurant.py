from monolith.database import db, Restaurant, Booking, Table
from datetime import datetime, timedelta

def is_busy_table(tab_id):
    qr = db.session.query(Restaurant).join(Restaurant.tables, aliased=True).filter(Table.id == tab_id).first()
    occupation_time = qr.occupation_time
    qr = db.session.query(Table).join(Table.bookings, aliased=True).filter(Table.id == tab_id).filter(Booking.booking_datetime >= datetime.now()+timedelta(hours=occupation_time)).first()
    return qr is not None