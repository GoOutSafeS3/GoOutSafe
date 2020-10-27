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
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    phone = db.Column(db.Integer)
    
    rest_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), default=None)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False
    is_health_authority = db.Column(db.Boolean, default=False)
    is_positive = db.Column(db.Boolean, default=False)
    positive_datetime = db.Column(db.DateTime)

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
    #r = db.relationship('User', backref='Restaurant')
    name = db.Column(db.Text(100))
    
    likes = db.Column(db.Integer) # will store the number of likes, periodically updated in background

    lat = db.Column(db.Float) # restaurant latitude
    lon = db.Column(db.Float) # restaurant longitude

    tables_number = db.Column(db.Integer) # number of tables
    tables_capacity = db.Column(db.Integer) # capacity for every table

    opening_hour_lunch = db.Column(db.Integer) # the opening hour for the lunch
    closing_hour_lunch = db.Column(db.Integer) # the closing hour for the lunch 

    opening_hour_dinner = db.Column(db.Integer) # the opening hour for the dinner
    closing_hour_dinner = db.Column(db.Integer) # the closing hour for the dinner 

    occupation_time = db.Column(db.Integer)

    closed_days = db.Column(db.Text(7)) # one number for every closing day (1-7 i.e. monday-sunday)

    phone = db.Column(db.Integer)

    cuisine_type = db.Column(db.Text(1000))
    menu = db.Column(db.Text(1000))

    def is_open(self, booking_datetime):
        now = datetime.datetime.now()
        lunch_opening = now.replace( hour=self.opening_hour_lunch, minute=0, second=0, microsecond=0 )
        lunch_closing = now.replace( hour=self.closing_hour_lunch, minute=0, second=0, microsecond=0 )

        dinner_opening = now.replace( hour=self.opening_hour_dinner, minute=0, second=0, microsecond=0 )
        dinner_closing = now.replace( hour=self.closing_hour_dinner, minute=0, second=0, microsecond=0 )

        booking = now.replace( hour=booking_datetime.hour, minute=booking_datetime.minute, second=0, microsecond=0 )

        return ( not(str(booking_datetime.weekday()+1) in self.closed_days ) ) and ( (lunch_opening <= booking <= lunch_closing) or (dinner_opening <= booking <= dinner_closing) )

    def get_id(self):
        return self.id

class Table(db.Model):
    __tablename__ = 'table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rest_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    capacity = db.Column(db.Integer)

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rest_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    person_number = db.Column(db.Integer)
    booking_datetime = db.Column(db.DateTime)
    table = db.Column(db.Integer, db.ForeignKey('table.id'))


class Like(db.Model):
    __tablename__ = 'like'
    
    liker_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    liker = relationship('User', foreign_keys='Like.liker_id')

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), primary_key=True)
    restaurant = relationship('Restaurant', foreign_keys='Like.restaurant_id')

    marked = db.Column(db.Boolean, default = False) # True iff it has been counted in Restaurant.likes 
