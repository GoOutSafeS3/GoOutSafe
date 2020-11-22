from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy.orm import relationship
import datetime as dt
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    phone = db.Column(db.Unicode(128), unique=True)
    ssn = db.Column(db.Unicode(128), unique=True, default=None)
    rest_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), default=None)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False
    is_health_authority = db.Column(db.Boolean, default=False)
    is_positive = db.Column(db.Boolean, default=False)
    positive_datetime = db.Column(db.DateTime)

    restaurant = relationship('Restaurant')

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    @property
    def is_operator(self):
        if self.rest_id is None:
            return False
        else:
            return True

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id

    def get_rest_id(self):
        return self.rest_id


class Restaurant(db.Model):

    __tablename__ = 'restaurant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text(100))
    rating_val = db.Column(db.Float, default=0) # will store the mean value of the rating
    rating_num = db.Column(db.Integer, default=0) # will store the number of ratings
    lat = db.Column(db.Float) # restaurant latitude
    lon = db.Column(db.Float) # restaurant longitude
    opening_hour_lunch = db.Column(db.Integer) # the opening hour for the lunch
    closing_hour_lunch = db.Column(db.Integer) # the closing hour for the lunch
    opening_hour_dinner = db.Column(db.Integer) # the opening hour for the dinner
    closing_hour_dinner = db.Column(db.Integer) # the closing hour for the dinner
    occupation_time = db.Column(db.Integer) # in hours the time of occupation of a table
    closed_days = db.Column(db.Text(7), default="") # one number for every closing day (1-7 i.e. monday-sunday)
    phone = db.Column(db.Integer)
    cuisine_type = db.Column(db.Text(1000))
    menu = db.Column(db.Text(1000))
    tables = relationship('Table')
    operators = relationship('User')

    def is_open(self, booking_datetime):
        """
        Given a datetime, check that the restaurant is open on that date
        """
        if str(booking_datetime.weekday()+1) in self.closed_days:
            return False

        now = datetime.datetime.now()

        booking = now.replace( hour=booking_datetime.hour, minute=booking_datetime.minute, second=0, microsecond=0 )

        if self.opening_hour_lunch is not None and self.opening_hour_lunch is not None:

            lunch_opening = now.replace( hour=self.opening_hour_lunch, minute=0, second=0, microsecond=0 )
            lunch_closing = now.replace( hour=self.closing_hour_lunch, minute=0, second=0, microsecond=0 )

            if lunch_opening <= booking <= lunch_closing:
                return True

        if self.opening_hour_dinner is not None and self.opening_hour_dinner is not None:

            dinner_opening = now.replace( hour=self.opening_hour_dinner, minute=0, second=0, microsecond=0 )
            dinner_closing = now.replace( hour=self.closing_hour_dinner, minute=0, second=0, microsecond=0 )

            if dinner_opening <= booking <= dinner_closing:
                return True

        return False

    def get_id(self):
        return self.id


class Table(db.Model):
    __tablename__ = 'table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rest_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    capacity = db.Column(db.Integer)
    restaurant = relationship('Restaurant')
    bookings = relationship('Booking')


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rest_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    people_number = db.Column(db.Integer)
    booking_datetime = db.Column(db.DateTime) # the time of  booking
    entrance_datetime = db.Column(db.DateTime, default = None) # the time of entry
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))
    user = relationship('User')
    restaurant = relationship('Restaurant')
    table = relationship('Table')


class Rating(db.Model):
    __tablename__ = 'Rating'
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rater = relationship('User', foreign_keys='Rating.rater_id')
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), primary_key=True)
    restaurant = relationship('Restaurant', foreign_keys='Rating.restaurant_id')
    rating = db.Column(db.Integer)
    marked = db.Column(db.Boolean, default = False) # True iff it has been counted in Restaurant.rating


class Notification(db.Model):
    """
    Table containing GoOutSafe notifications

    Fields of the table:

    - notification_id: (Integer) number representing the notification

    - user_positive_id: (Integer) useful in the event of a notification for a positive user
     addressed to an operator or customer.

    - rest_closed_name: (String) this field indicates a restaurant that has been deleted
    from the system. it is useful to communicate this to customers who had an
    active reservation in that restaurant.

    - user_positive_email: (String) customer email that has been marked as positive.
     Useful to communicate the customer email to the operator,
     who will have to cancel the customer reservation.

    - user_positive_name: (String) customer name (firstname + lastname) that has been
     marked as positive. Useful to communicate the customer name to the
     operator, who will have to cancel the customer reservation.

    - user_booking_date: (DateTime) customer booking date that has been
     marked as positive. Useful to communicate the booking to delete.

    - user_notified_id: (Integer) id of the user who will receive the notification.

    - already_read: (Boolean) representing whether the notification has been read.

    - datetime: (DateTime) day on which the notification was generated.

    - operator_notification_type: (Integer) type of operator notification,
      depending on the type, a certain message will be shown on the page.

    - customer_notification_type: (Integer) type of customer notification,
      depending on the type, a certain message will be shown on the page.

    """
    __tablename__ = 'notification'

    notification_id = db.Column(db.Integer, autoincrement=True, primary_key = True)
    user_positive_id = db.Column(db.Integer, db.ForeignKey('user.id') )
    rest_closed_name = db.Column(db.String, default=None)
    user_positive_email = db.Column(db.String, default=None)
    user_positive_name = db.Column(db.String, default=None)
    user_booking_date = db.Column(db.DateTime, default=None)
    user_notified_id= db.Column(db.Integer, db.ForeignKey('user.id'))
    already_read = db.Column(db.Boolean, default=False)
    datetime = db.Column(db.DateTime, default = None)
    operator_notification_type = db.Column(db.Integer, default=0)
    customer_notification_type = db.Column(db.Integer, default=0)

