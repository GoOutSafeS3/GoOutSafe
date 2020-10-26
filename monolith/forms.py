from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired, Email, InputRequired
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