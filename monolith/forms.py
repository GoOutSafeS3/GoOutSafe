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
    email = EmailField('email', validators=[DataRequired(), Email()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    password_repeat = f.PasswordField('repeat password', validators=[DataRequired()])
    telephone = f.StringField('telephone', validators=[DataRequired()]) #GB add validator 
    dateofbirth = f.DateField('dateofbirth', format='%d/%m/%Y')

    restaurant_phone = f.IntegerField('restaurant_phone', validators=[DataRequired()])
    restaurant_latitude = f.FloatField('restaurant_latitude', validators=[DataRequired()])
    restaurant_longitude = f.FloatField('restaurant_longitude', validators=[DataRequired()])

    display = ['email', 'firstname', 'lastname', 'password','password_repeat', 'telephone', 'dateofbirth', 'restaurant_phone', 'restaurant_latitude', 'restaurant_longitude']