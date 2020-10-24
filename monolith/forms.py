from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired, Email
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    password_repeat = f.PasswordField('repeat password', validators=[DataRequired()])
    telephone = f.StringField('telephone', validators=[DataRequired()]) #GB add validator 
    dateofbirth = f.DateField('dateofbirth', format='%d/%m/%Y')

    display = ['email', 'firstname', 'lastname', 'password','password_repeat', 'telephone', 'dateofbirth']


class OperatorForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    firstname = f.StringField('Firstname', validators=[DataRequired()])
    lastname = f.StringField('Lastname', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    password_repeat = f.PasswordField('Repeat password', validators=[DataRequired()])
    telephone = f.StringField('Telephone', validators=[DataRequired()]) #GB add validator
    dateofbirth = f.DateField('Date Of Birth', format='%d/%m/%Y')

    restaurant_name = f.StringField('Restaurant Name',validators=[DataRequired()])
    restaurant_phone = f.IntegerField('Restaurant Phone', validators=[DataRequired()])
    restaurant_latitude = f.FloatField('Restaurant latitude', validators=[DataRequired()])
    restaurant_longitude = f.FloatField('Restaurant Longitude', validators=[DataRequired()])

    display = ['email', 'firstname', 'lastname', 'password','password_repeat', 'telephone', 'dateofbirth','restaurant_name','restaurant_phone', 'restaurant_latitude', 'restaurant_longitude']