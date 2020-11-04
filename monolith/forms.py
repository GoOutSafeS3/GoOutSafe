from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired, Email, InputRequired, NumberRange, optional
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    """
    Form to login
    """
    email = f.StringField('Email', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])

    display = ['email', 'password']


class UserForm(FlaskForm):
    """
    Form to insert a user's data (profile)
    """
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = f.StringField('Firstname', validators=[DataRequired()])
    lastname = f.StringField('Lastname', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    password_repeat = f.PasswordField('Repeat Password', validators=[DataRequired()])
    telephone = f.StringField('Telephone', validators=[DataRequired()]) 
    dateofbirth = f.DateField('Date Of Birth', format='%d/%m/%Y')
    ssn = f.StringField('SSN (if available)', validators=[])
    submit = f.SubmitField('Confirm')
    display = ['email', 'firstname', 'lastname', 'password','password_repeat', 'telephone', 'dateofbirth', 'ssn']


class EditUserForm(FlaskForm):
    """
    Form to edit a user's data (profile)
    """
    firstname = f.StringField('Firstname')
    lastname = f.StringField('Lastname')
    new_password = f.PasswordField('Password')
    old_password = f.PasswordField('Old Password', validators=[DataRequired()])
    password_repeat = f.PasswordField('Repeat Password')
    telephone = f.StringField('Telephone')
    dateofbirth = f.DateField('Date Of Birth', format='%d/%m/%Y')
    ssn = f.StringField('SSN (if available)', validators=[])
    submit = f.SubmitField('Confirm')


class OperatorForm(FlaskForm):
    """
    Form to insert a operator's data (profile)
    """
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = f.StringField('Firstname', validators=[DataRequired()])
    lastname = f.StringField('Lastname', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    password_repeat = f.PasswordField('Repeat Password', validators=[DataRequired()])
    telephone = f.StringField('Telephone', validators=[DataRequired()]) 
    dateofbirth = f.DateField('Date Of Birth', format='%d/%m/%Y')

    restaurant_name = f.StringField('Restaurant Name',validators=[DataRequired()])
    restaurant_phone = f.StringField('Restaurant Phone', validators=[DataRequired()])
    restaurant_latitude = f.FloatField('Restaurant latitude', validators=[InputRequired()])
    restaurant_longitude = f.FloatField('Restaurant Longitude', validators=[InputRequired()])

    display = ['email', 'firstname', 'lastname', 'password','password_repeat', 'telephone', 'dateofbirth','restaurant_name','restaurant_phone', 'restaurant_latitude', 'restaurant_longitude']


class RestaurantEditForm(FlaskForm):
    """
    Form to insert/edit a restaurant
    """
    name = f.StringField('Restaurant Name',validators=[DataRequired()])
    phone = f.StringField('Restaurant Phone', validators=[DataRequired()])
    lat = f.FloatField('Restaurant Latitude', validators=[InputRequired()])
    lon = f.FloatField('Restaurant Longitude', validators=[InputRequired()])
    opening_hour_lunch = f.IntegerField('First opening hour (first submitable booking time)', validators=[optional()])  # the opening hour for the lunch
    closing_hour_lunch = f.IntegerField('First closing hour (last submitable booking time)', validators=[optional()]) # the closing hour for the lunch
    opening_hour_dinner = f.IntegerField('Second opening hour (if available)', validators=[optional()]) # the opening hour for the dinner
    closing_hour_dinner = f.IntegerField('Second closing hour (if available)', validators=[optional()]) # the closing hour for the dinner
    occupation_time = f.IntegerField('Time for a table to be clear again', validators=[InputRequired()])
    closed_days = f.SelectMultipleField('Closed days',  choices=[("1","Monday"), ("2","Tuesday"), ("3","Wednesday"), ("4","Thursday"),("5","Friday"), ("6","Saturday"),("7","Sunday")], validators=[InputRequired()])
    cuisine_type = f.StringField('Cousine type',validators=[DataRequired()])
    menu = f.StringField('Restaurant menu',validators=[DataRequired()])

    display = ['name', 'phone', 'lat', 'lon','opening_hour_lunch', 'closing_hour_lunch', 'opening_hour_dinner','closing_hour_dinner','occupation_time', 'closed_days', 'cuisine_type','menu']


class TableAddForm(FlaskForm):
    """
    Form to insert/edit a table in a restaurant
    """
    capacity = f.IntegerField('Table capacity', validators=[InputRequired()])
    display = ['capacity']

class RatingAddForm(FlaskForm):
    """
    Form to add a rating in a restaurant
    """
    rating = f.IntegerField('Restaurant rating', validators=[InputRequired()])
    display = ['rating']

class BookingForm(FlaskForm):
    """
    Form to insert/edit a reservation
    """
    number_of_people = f.IntegerField("Number of people", validators=[InputRequired(), NumberRange(min=1)])
    booking_date = f.DateField('Date', format='%d/%m/%Y')
    booking_hr = f.SelectField('Hour', choices=range(0,24))
    booking_min = f.SelectField('Minutes', choices=range(0,60,15))

    display = ['number_of_people','booking_date','booking_hr','booking_min']


class BookingList(FlaskForm):
    """
    Form to find all the reservations in a specific period
    """
    from_date = f.DateField('From Date', format='%d/%m/%Y')
    from_hr = f.SelectField('Hour', choices=range(0,24))
    from_min = f.SelectField('Minutes', choices=range(0,60,15))
    to_date = f.DateField('To Date', format='%d/%m/%Y')
    to_hr = f.SelectField('Hour', choices=range(0,24))
    to_min = f.SelectField('Minutes', choices=range(0,60,15))

    display = ['from_date','from_hr','from_min','to_date','to_hr','to_min']


class SearchUserForm(FlaskForm):
    """
    Form to find a user by his/her identifiers
    """
    email = f.StringField('Email')
    telephone = f.StringField('Telephone')
    ssn = f.StringField('SSN')

    display = ['email', 'telephone', "ssn"]


class SearchRestaurantForm(FlaskForm):
    """
    Form to find all the restaurants that respect certain parameters expressed in the filters
    """
    name = f.StringField('Restaurant Name')
    opening_time = f.SelectField('Open at', choices=["Not Specified"]+([x for x in range(24)]))
    open_day = f.SelectField('Open on',  choices=[("0","Not Specified"), ("1","Monday"), ("2","Tuesday"), ("3","Wednesday"), ("4","Thursday"),("5","Friday"), ("6","Saturday"),("7","Sunday")])
    cuisine_type = f.StringField('Cousine type')
    menu = f.StringField('Restaurant menu')

    display = ['name', 'opening_time', 'open_day', 'cuisine_type', 'menu']
