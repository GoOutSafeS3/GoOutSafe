from datetime import timedelta, datetime
from flask import Blueprint, redirect, render_template, request, flash, make_response
from flask_login import login_required, logout_user, current_user, login_user
from monolith.utilities.contact_tracing import get_user_contacts
from werkzeug.security import check_password_hash
from monolith.auth import health_authority_required, admin_required
from monolith.database import User, db, Restaurant, Booking
from monolith.forms import UserForm, OperatorForm, LoginForm, EditUserForm
from monolith.utilities.notification import add_notification_restaurant_closed

users = Blueprint('users', __name__)


@users.route('/users')
@admin_required
def _users():
    """ Returns the list of registered users

    You must be logged in as admin

    Error status codes:
        401 -- If a user other than admin tries to view it
    """
    users = db.session.query(User)
    return render_template("users.html", users=users)


@users.route('/reservations', methods=['GET', 'POST'])
@login_required
def user_bookings():
    """ Displays the current user's future bookings list.

    You must be logged in as a customer

    Error status codes:
        404 -- If the current user is not a customer
    """
    if current_user.is_admin or current_user.is_health_authority or current_user.rest_id is not None:
        return make_response(render_template('error.html', error='404'),404)

    now = datetime.now()

    qry = db.session.query(Booking,Restaurant)\
                    .filter(Booking.rest_id == Restaurant.id)\
                    .filter(Booking.user_id == current_user.id)\
                    .filter(Booking.booking_datetime >= now)\
                    .order_by(Booking.booking_datetime).all()
    
    if qry == []:
        flash("There are no reservations", "warning")

    return make_response(render_template('bookings.html', bookings=qry, title="Your Reservations"),200)


@users.route('/delete', methods=['GET', 'POST'])
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
            email, password = form.data['email'], form.data['password']
            if current_user.email != email:
                flash('Wrong email', 'error')
                return make_response(render_template('delete_profile.html', form=form, title="Unregister"), 400)
            user = db.session.query(User).filter(current_user.email == User.email).first()
            checked = check_password_hash(current_user.password, password)
            if user is not None and checked:
                if current_user.is_positive:
                    flash('You cannot delete your data as long as you are positive','error')
                    return redirect('/', code=302)
                else:
                    rest = Restaurant.query.filter_by(id=current_user.rest_id).first()
                    logout_user()
                    db.session.delete(user)
                    if rest is not None:
                        bookings = Booking.query.filter_by(rest_id=rest.id).all()
                        for b in bookings: # send the notifications 
                            if b.booking_datetime >= datetime.today():
                                add_notification_restaurant_closed(rest, b.user_id, b.booking_datetime)
                                db.session.delete(b)
                        db.session.delete(rest)
                    try:
                        db.session.commit()
                        flash('Your account has been deleted', 'success')
                        return redirect('/', code=302)
                    except:
                        db.session.rollback()
                        flash('There was a problem, please try again', 'error')
                        return make_response(render_template('delete_profile.html', form=form, title="Unregister"), 400)
            else:
                flash('Wrong email or password','error')
                return make_response(render_template('delete_profile.html', form=form, title="Unregister"),400)
        flash('Bad form','error')
        return make_response(render_template('delete_profile.html', form=form, title="Unregister"),400)
    return make_response(render_template('delete_profile.html', form=form, title="Unregister"),200)


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
            password = request.form['password']
            password_repeat = request.form['password_repeat']
            if password != password_repeat:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('form.html', form=form, title="Sign in!"),200)

            userGetMail = User.query.filter_by(email=form.email.data).first()
            userGetPhone = User.query.filter_by(phone=form.telephone.data).first()
            userGetSSN = None

            if form.ssn.data is not None and form.ssn.data != "":
                userGetSSN = User.query.filter_by(ssn=form.ssn.data).first()
            else:
                form.ssn.data = None

            if userGetMail is None and userGetPhone is None and userGetSSN is None:
                new_user = User()
                new_user.firstname = form.firstname.data
                new_user.lastname = form.lastname.data
                new_user.email = form.email.data
                new_user.set_password(form.password.data)
                new_user.phone = form.telephone.data
                today = datetime.today()
                b_date = request.form["dateofbirth"]
                day, month, year = (int(x) for x in b_date.split('/'))
                birth_date = today.replace(year=year, month=month, day=day)
                if birth_date > today:
                    flash('Date Of Birth error', 'error')
                    return make_response(render_template('form.html', form=form, title="Sign in!"), 400)
                new_user.dateofbirth = form.dateofbirth.data
                new_user.ssn = form.ssn.data
                try:
                    new_user.set_password(form.password.data)  # pw should be hashed with some salt
                    db.session.add(new_user)
                    db.session.commit()
                except:
                    flash('User not inserted','error')
                    return make_response(render_template('form.html', form=form, title="Sign in!"),500)
            else:
                flash('Existing user', 'error')
                return make_response(render_template('form.html', form=form, title="Sign in!"),400)

            if new_user is not None and new_user.authenticate(password):
                login_user(new_user)
            flash('User registerd succesfully', 'success')
            return redirect("/")

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
    form = OperatorForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            password = request.form['password']
            password_repeat = request.form['password_repeat']
            if password != password_repeat:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('form.html', form=form, title="Sign in!"),200)

            userRestaurant = Restaurant.query.filter_by(name=form.restaurant_name.data).first()

            userGetMail = User.query.filter_by(email=form.email.data).first()
            userGetPhone = User.query.filter_by(phone=form.telephone.data).first()

            if userRestaurant is None:
                new_rest = Restaurant()
                new_rest.name = form.restaurant_name.data
                new_rest.lat = form.restaurant_latitude.data
                new_rest.lon = form.restaurant_longitude.data
                new_rest.phone = form.restaurant_phone.data
                if userGetMail is None and userGetPhone is None:
                    new_user = User()
                    new_user.firstname = form.firstname.data
                    new_user.lastname = form.lastname.data
                    new_user.email = form.email.data
                    new_user.set_password(form.password.data)
                    new_user.phone = form.telephone.data
                    today = datetime.today()
                    b_date = request.form["dateofbirth"]
                    day, month, year = (int(x) for x in b_date.split('/'))
                    birth_date = today.replace(year=year, month=month, day=day)
                    if birth_date > today:
                        flash('Date Of Birth error', 'error')
                        return make_response(render_template('form.html', form=form, title="Sign in!"), 400)
                    new_user.dateofbirth = form.dateofbirth.data
                    try:
                        db.session.add(new_rest)
                        db.session.commit()
                        new_user.rest_id = new_rest.id
                        db.session.add(new_user)
                        db.session.commit()

                    except:
                        flash('New operator and Restaurant not inserted','error')
                        return make_response(render_template('form.html', form=form, title="Sign in!"),500)
                else:
                    flash('Existing operator', 'error')
                    return make_response(render_template('form.html', form=form, title="Sign in!"), 400)
            else:
                flash('Existing restaurant', 'error')
                return make_response(render_template('form.html', form=form, title="Sign in!"), 400)

            if new_user is not None and new_user.authenticate(password):
                login_user(new_user)
            flash('Restaurant registered succesfully! Click Settings->Edit Restaurant to add your restaurant information!', 'success')
            return redirect("/")

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

    user = User.query.filter_by(id = current_user.id).first()
    form = EditUserForm()

    if request.method == 'POST':
        new_password = form.new_password.data
        password_repeat = form.password_repeat.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        telephone = form.telephone.data
        dateofbirth = form.dateofbirth.data
        ssn = form.ssn.data
        password = form.old_password.data

        if password == '':
            flash('Insert password to modify the account','error')
            return make_response(render_template('edit_profile.html', form=form, user=user, title="Modify your profile!"), 400)

        checked = check_password_hash(current_user.password, password)
        if checked:
            if new_password != password_repeat:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('edit_profile.html', form=form, user=user, title="Modify your profile!"), 400)

            userGetPhone = User.query.filter(User.id != current_user.id).filter_by(phone=telephone).first()
            userGetSSN = None

            if ssn is not None and ssn != "":
                userGetSSN = User.query.filter(User.id != current_user.id).filter_by(ssn=form.ssn.data).first()
            else:
                form.ssn.data = None

            if userGetPhone is None and userGetSSN is None:

                if new_password != "" and password_repeat == new_password:
                    current_user.set_password(new_password)
                if firstname != "":
                    current_user.firstname = firstname
                if lastname != "":
                    current_user.lastname = lastname
                if telephone != "":
                    current_user.phone = telephone
                if dateofbirth is not None and dateofbirth != "":
                    today = datetime.today()
                    b_date = request.form["dateofbirth"]
                    day, month, year = (int(x) for x in b_date.split('/'))
                    birth_date = today.replace(year=year, month=month, day=day)
                    if birth_date > today:
                        flash('Date Of Birth error', 'error')
                        return make_response(render_template('edit_profile.html', user=user, form=form, title="Modify your profile!"),400)
                    current_user.dateofbirth = dateofbirth
                if ssn != "":
                    current_user.ssn = ssn
                db.session.commit()

                flash('Profile modified', 'success')
                return redirect("/")

            else:
                flash('A user already exists with this data', 'error')
                return make_response(render_template('edit_profile.html', user=user, form=form, title="Modify your profile!"), 400)

        else:
            flash('Uncorrect password', 'error')
            return make_response(render_template('edit_profile.html', form=form, user=user, title="Modify your profile!"), 400)

    return render_template('edit_profile.html', form=form, user=user, title="Modify your profile!")