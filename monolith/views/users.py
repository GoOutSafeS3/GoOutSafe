from datetime import date, timedelta, datetime
from flask import Blueprint, redirect, render_template, request, flash, make_response
from flask_login import login_required, logout_user, current_user, login_user
from werkzeug.security import check_password_hash, generate_password_hash
from monolith.auth import health_authority_required, admin_required, User
from monolith.gateway import get_getaway
from monolith.forms import UserForm, OperatorForm, LoginForm, EditUserForm
from dotmap import DotMap

users = Blueprint('users', __name__)


@users.route('/users')
@admin_required
def _users():
    """ Returns the list of registered users

    You must be logged in as admin

    Error status codes:
        401 -- If a user other than admin tries to view it
    """
    users, status = get_getaway().get_users()
    if users is None or status != 200:
        return render_template("error.html", error=500), 500
    
    return render_template("users.html", users=users)


@users.route('/reservations', methods=['GET', 'POST'])
@login_required
def user_bookings():
    """ Displays the current user's future bookings list.

    You must be logged in as a customer

    Error status codes:
        404 -- If the current user is not a customer
        500 -- An error occured
    """
    if current_user.is_admin or current_user.is_health_authority or current_user.is_operator:
        return make_response(render_template('error.html', error='404'),404)
    
    now = datetime.now().replace(hour=0,minute=0, second=0, microsecond=0)
    bookings, status_code = get_getaway().get_bookings(user=current_user.id, begin=now)

    if status_code is None or status_code != 200:
        flash("Sorry, an error occured. Please, try again.","error")
        bookings = []
    elif bookings is None or bookings==[]:
        bookings = []
        flash("No reservations were found","warning")

    return make_response(render_template('bookings.html', bookings=bookings, title="Your Reservations"),200)


@users.route('/delete', methods=['GET', 'POST','DELETE'])
@login_required
def delete_user():
    """ Delete the current user profile and log out
    
    The user must confirm the request by entering email and password.

    The request is approved only if the user is not positive.

    If the user is an operator, the restaurant is also deleted. 
    In that case, a notification is sent to all users who had active bookings,
    and bookings are canceled.

    The functionality is not active for the health authority or for the admin.

    Error status codes:
        400 -- The request is not valid, the form is filled out incorrectly or a generic error has occurred
        401 -- The current user is not a customer or operator

    Success codes:
        200 -- The form is sent
        302 -- The elimination was carried out
    """
    if current_user.is_admin or current_user.is_health_authority:
        return make_response(render_template('error.html', error='401'),401)

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            users, status_code = get_getaway().get_users(email=form.data['email'])
            if users is not None:
                email, password = form.data['email'], form.data['password']
                user = users[0].toDict()
            else:
                flash('Wrong email', 'error')
                return make_response(render_template('delete_profile.html', form=form, title="Unregister"), 400)
            checked = check_password_hash(user['password'],password)
            if checked:
                usr, status = get_getaway().delete_user(user['id'])
                if status == 204:
                    flash('Account deleted','success')
                    logout_user(current_user)
                    return make_response(render_template('homepage.html'), 200)
                if status == 400:
                    flash('Please try again', 'warning')
                    return make_response(render_template('error.html', title="Unregister"), 400)
                if status == 500:
                    flash('Please try again', 'error')
                    return make_response(render_template('error.html', title="Unregister"), 500)
            else:
                flash('Wrong password','error')
                return make_response(render_template('delete_profile.html', form=form, title="Unregister"),400)
        else:
            flash('Bad form','error')
            return make_response(render_template('delete_profile.html', form=form, title="Unregister"),400)
    return render_template('delete_profile.html', form=form, title="Unregister")


@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
    """ Create a customer account and login
    
    Error status codes:
        400 -- The request is not valid, the form is filled out incorrectly, a user with the same identifiers already exists or a generic error has occurred
        500 -- A db error
    Success codes:
        200 -- The form is sent
        302 -- The creation was carried out
    """
    form = UserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            json = DotMap()
            form.populate_obj(json)
            json = json.toDict()

            if json['password'] != json['password_repeat']:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('form.html', form=form, title="Sign in!"),200)

            user = {'firstname': json['firstname'], 'lastname': json['lastname'], 'email': json['email'],
                    'password': generate_password_hash(form.password.data), 'phone': json['telephone'],
                    'rest_id': None, 'is_operator': False, 'ssn': json['ssn'], 'is_admin': False,
                    'dateofbirth' : json['dateofbirth'], 'is_health_authority': False, 'is_positive': False}

            resp, status_code = get_getaway().create_user(userdata=user)
            if resp is None or status_code is None:
                flash("Sorry, an error occured. Please, try again.", "error")
                return make_response(render_template('form.html', form=form, title="Sign in!"), 500)
            if status_code == 200 or status_code == 201:
                usr = User(user['id'], user['is_operator'], user['is_admin'], user['is_health_authority'],
                           user['password'], user['rest_id'], user['is_positive'])
                login_user(usr)
                flash('User registerd succesfully', 'success')
                return redirect("/")
            else:
                return make_response(render_template("error.html", error=status_code), status_code)

    return render_template('form.html', form=form, title="Sign in!")


@users.route('/create_operator', methods=['GET', 'POST'])
def create_operator():
    """ Create an operator account and login
    
    Error status codes:
        400 -- The request is not valid, the form is filled out incorrectly, a user with the same identifiers already exists or a generic error has occurred
        500 -- A db error
    Success codes:
        200 -- The form is sent
        302 -- The creation was carried out
    """
    form = UserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            json = DotMap()
            form.populate_obj(json)
            json = json.toDict()

            if json['password'] != json['password_repeat']:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('form.html', form=form, title="Sign in!"), 200)

            user = {'firstname': json['firstname'], 'lastname': json['lastname'], 'email': json['email'],
                    'password': generate_password_hash(form.password.data), 'phone': json['telephone'],
                    'rest_id': None, 'is_operator': True, 'ssn': json['ssn'], 'is_admin': False,
                    'dateofbirth': json['dateofbirth'], 'is_health_authority': False, 'is_positive': False}

            resp, status_code = get_getaway().create_user(userdata=user)
            if resp is None or status_code is None:
                flash("Sorry, an error occured. Please, try again.", "error")
                return make_response(render_template('form.html', form=form, title="Sign in!"), 500)
            if status_code == 200:
                usr = User(user['id'], user['is_operator'], user['is_admin'], user['is_health_authority'],
                           user['password'], user['rest_id'], user['is_positive'])
                login_user(usr)
                flash('User registerd succesfully', 'success')
                return redirect("/")
            else:
                return make_response(render_template("error.html", error=status_code), status_code)

        return render_template('form.html', form=form, title="Sign in!")


@users.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """ Edit the current user profile
    
    The user must confirm the request by entering the password.

    The functionality is not active for the health authority or for the admin.

    Error status codes:
        400 -- the data entered is incorrect or a user with the same identifiers already exists
        401 -- The current user is not a customer or operator

    Success codes:
        200 -- The form is sent
        302 -- The update was carried out
    """

    if current_user.is_admin or current_user.is_health_authority:
        return make_response(render_template('error.html', error='401'),401)

    form = EditUserForm()

    if request.method == 'POST':
        json = DotMap()
        form.populate_obj(json)
        json = json.toDict()

        user_to_edit, status_code = get_getaway().get_user(current_user.id)
        if status_code != 200:
            flash('Try again', 'warning')
            return make_response(render_template('edit_profile.html', form=form, title="Modify you profile!"), 400)

        if json['old_password'] == '' or json['old_password'] is None:
            flash('Insert password to modify the account', 'error')
            return make_response(render_template('edit_profile.html', form=form, title="Modify your profile!"), 400)

        checked = check_password_hash(current_user.password, json['old_password'])
        if checked:
            if 'new_password' in json and 'password_repeat' in json:
                if json['new_password'] is not None and json['password_repeat'] is not None:
                    if json['new_password'] != json['password_repeat']:
                        flash('Passwords do not match', 'warning')
                        return make_response(render_template('edit_profile.html', form=form, title="Modify you profile!"), 400)
                    else:
                        user_to_edit['password'] = generate_password_hash(json['new_password'])

                elif (json['new_password'] is None and json['password_repeat'] is not None) or (json['new_password'] is not None and json['password_repeat'] is None):
                    flash('Insert both password', 'warning')
                    return make_response(render_template('edit_profile.html', form=form, title="Modify you profile!"), 400)

            if 'lastname' in json and json['lastname'] is not None:
                user_to_edit['lastname'] = json['lastname']

            if 'firstname' in json and json['firstname'] is not None:
                user_to_edit['firstname'] = json['firstname']

            response_user, status_code = get_getaway().edit_user(current_user.id, user_to_edit)
            if status_code == 200:
                flash('Profile modified with success', 'success')
                return redirect("/")
            elif status_code == 400:
                flash('Bad request', 'warning')
                return make_response(render_template("error.html", error=status_code), status_code)
            elif status_code == 500:
                flash("Sorry, an error occured. Please, try again", "error")
                return make_response(render_template("error.html", error=status_code), status_code)
        else:
            flash('Uncorrect password', 'error')
            return make_response(render_template('edit_profile.html', form=form, title="Modify your profile!"), 400)

    return render_template('edit_profile.html', form=form,title="Modify your profile!")