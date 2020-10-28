from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired, Email, InputRequired, NumberRange
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = f.StringField('Firstname', validators=[DataRequired()])
    lastname = f.StringField('Lastname', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    password_repeat = f.PasswordField('Repeat Password', validators=[DataRequired()])
    telephone = f.IntegerField('Telephone', validators=[InputRequired()]) 
    dateofbirth = f.DateField('Date Of Birth', format='%d/%m/%Y')

    display = ['email', 'firstname', 'lastname', 'password','password_repeat', 'telephone', 'dateofbirth']


class OperatorForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = f.StringField('Firstname', validators=[DataRequired()])
    lastname = f.StringField('Lastname', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    password_repeat = f.PasswordField('Repeat Password', validators=[DataRequired()])
    telephone = f.IntegerField('Telephone', validators=[InputRequired()]) #GB add validator
    dateofbirth = f.DateField('Date Of Birth', format='%d/%m/%Y')

    restaurant_name = f.StringField('Restaurant Name',validators=[DataRequired()])
    restaurant_phone = f.IntegerField('Restaurant Phone', validators=[InputRequired()])
    restaurant_latitude = f.FloatField('Restaurant latitude', validators=[InputRequired()])
    restaurant_longitude = f.FloatField('Restaurant Longitude', validators=[InputRequired()])

    display = ['email', 'firstname', 'lastname', 'password','password_repeat', 'telephone', 'dateofbirth','restaurant_name','restaurant_phone', 'restaurant_latitude', 'restaurant_longitude']

class RestaurantEditForm(FlaskForm):
    name = f.StringField('Restaurant Name',validators=[DataRequired()])
    phone = f.IntegerField('Restaurant Phone', validators=[InputRequired()])
    lat = f.FloatField('Restaurant latitude', validators=[InputRequired()])
    lon = f.FloatField('Restaurant Longitude', validators=[InputRequired()])

    opening_hour_lunch = f.IntegerField('Opening hour for lunch', validators=[InputRequired()])  # the opening hour for the lunch
    closing_hour_lunch = f.IntegerField('Closing hour for lunch', validators=[InputRequired()]) # the closing hour for the lunch 

    opening_hour_dinner = f.IntegerField('Opening hour for dinner', validators=[InputRequired()]) # the opening hour for the dinner
    closing_hour_dinner = f.IntegerField('Closing hour for dinner', validators=[InputRequired()]) # the closing hour for the dinner 

    occupation_time = f.IntegerField('Time for a table to be clear again', validators=[InputRequired()])

    closed_days = f.SelectMultipleField('Closed days',  choices=[("1","Monday"), ("2","Tuesday"), ("3","Wednesday"), ("4","Thursday"),("5","Friday"), ("6","Saturday"),("7","Sunday")], validators=[InputRequired()])

    cuisine_type = f.StringField('Cousine type',validators=[DataRequired()])
    menu = f.StringField('Restaurant menu',validators=[DataRequired()])
    display = ['name', 'phone', 'lat', 'lon','opening_hour_lunch', 'closing_hour_lunch', 'opening_hour_dinner','closing_hour_dinner','occupation_time', 'closed_days', 'cuisine_type','menu']


class BookingForm(FlaskForm):
    number_of_person = f.IntegerField("Number of Person", validators=[InputRequired(), NumberRange(min=1)])
    booking_date = f.DateField('Date', format='%d/%m/%Y')
    booking_hr = f.SelectField('Hour', choices=range(0,23))
    booking_min = f.SelectField('Minutes', choices=range(0,60,15))
    display = ['number_of_person','booking_date','booking_hr','booking_min']

class BookingList(FlaskForm):
    from_date = f.DateField('From Date', format='%d/%m/%Y')
    from_hr = f.SelectField('Hour', choices=range(0,24))
    from_min = f.SelectField('Minutes', choices=range(0,60,15))

    to_date = f.DateField('To Date', format='%d/%m/%Y')
    to_hr = f.SelectField('Hour', choices=range(0,24))
    to_min = f.SelectField('Minutes', choices=range(0,60,15))

    display = ['from_date','from_hr','from_min','to_date','to_hr','to_min']

