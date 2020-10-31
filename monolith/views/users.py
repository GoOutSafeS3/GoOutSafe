from flask import Blueprint, redirect, render_template, request, flash, make_response
from flask_login import login_required, logout_user, current_user, login_user
from sqlalchemy.orm import aliased

from monolith.auth import admin_required, is_admin, operator_required, health_authority_required
from monolith.forms import UserForm, OperatorForm, LoginForm
from monolith.database import User, db, Restaurant, Booking
from datetime import timedelta, datetime

users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    if is_admin():
        users = db.session.query(User)
        return render_template("users.html", users=users)

def get_user_contacts(user_id, date_begin, date_end):
    result = db.session.execute(
    """SELECT * FROM user AS User1 WHERE User1.id IN (
    SELECT user_id FROM booking AS Booking1 WHERE EXISTS(
        SELECT * FROM booking AS Booking2
        JOIN restaurant AS R ON Booking2.rest_id = R.id
        WHERE
            Booking2.rest_id = Booking1.rest_id AND
            Booking2.user_id = :user_id AND
            datetime(Booking2.booking_datetime) >= datetime(:date_begin) AND
            datetime(Booking2.booking_datetime) <= datetime(:date_end) AND
            datetime(Booking2.booking_datetime) <= datetime(Booking1.booking_datetime) + strftime('%H', R.occupation_time) AND
            datetime(Booking1.booking_datetime) <= datetime(Booking2.booking_datetime) + strftime('%H', R.occupation_time)
    ) AND Booking1.user_id != :user_id)""",
        {"user_id": user_id, "date_begin": date_begin, "date_end": date_end}).\
        fetchall()

    return result

@users.route('/users/<int:user_id>/contacts')
@health_authority_required
def user_contacts(user_id):
    return render_template("users.html",
        users=get_user_contacts(user_id, datetime.today() - timedelta(days=14), datetime.today()))


@users.route('/reservations', methods=['GET', 'POST'])
@login_required
def user_bookings():
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
    if current_user.is_admin or current_user.is_health_authority:
        return make_response(render_template('error.html', error='401'),401)
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email, password = form.data['email'], form.data['password']
            q = db.session.query(User).filter(User.email == email)
            user = q.first()
            if user is not None and user.authenticate(password) and current_user.id == user.id:
                if current_user.is_positive:
                    flash('You cannot delete your data as long as you are positive','error')
                else:
                    q_r = db.session.query(Restaurant).filter_by(id = user.rest_id)	
                    rest = q_r.first()
                    logout_user()
                    db.session.delete(user)
                    if rest is not None:	
                        db.session.delete(rest)
                    db.session.commit()
                    flash('Your account has been deleted','success')
                return redirect('/', code=302)
            flash('Wrong email or password','error')
            return make_response(render_template('form.html', form=form, title="Unregister"),400)
        flash('Bad form','error')
        return make_response(render_template('form.html', form=form, title="Unregister"),400)
    return make_response(render_template('form.html', form=form, title="Unregister"),200)

@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
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
                new_user.dateofbirth = form.dateofbirth.data
                new_user.ssn = form.ssn.data
                try:
                    new_user.set_password(form.password.data)  # pw should be hashed with some salt
                    db.session.add(new_user)
                    db.session.commit()
                except: # Remove if coverage < 90%
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
                    new_user.dateofbirth = form.dateofbirth.data
                    try:
                        # pw should be hashed with some salt
                        db.session.add(new_rest)
                        db.session.commit()
                        new_user.rest_id = new_rest.id
                        db.session.add(new_user)
                        db.session.commit()

                    except: # Remove if coverage < 90%
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
            flash('Restaurant registered succesfully', 'success')
            return redirect("/")

    return render_template('form.html', form=form, title="Sign in!")

@users.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_user():

    if current_user.is_admin or current_user.is_health_authority:
        return make_response(render_template('error.html', error='401'),401)

    user = db.session.query(User).filter_by(id = current_user.id).first()

    if user is None: #remove if coverage <90%
        return make_response(render_template('error.html', error='404'), 404)

    user.telephone = user.phone
    form = UserForm(obj=user)

    if request.method == 'POST':

        if form.validate_on_submit():
            password = request.form['password']
            password_repeat = request.form['password_repeat']
            if password != password_repeat:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('form.html', form=form, title="Modify your profile!"),200)

            userGetMail = User.query.filter(User.id != current_user.id).filter_by(email=form.email.data).first()
            userGetPhone = User.query.filter(User.id != current_user.id).filter_by(phone=form.telephone.data).first()
            userGetSSN = None

            if form.ssn.data is not None and form.ssn.data != "":
                userGetSSN = User.query.filter(User.id != current_user.id).filter_by(ssn=form.ssn.data).first()
            else:
                form.ssn.data = None

            if userGetMail is None and userGetPhone is None and userGetSSN is None:
                user.firstname = form.firstname.data
                user.lastname = form.lastname.data
                user.email = form.email.data
                user.set_password(form.password.data)
                user.phone = form.telephone.data
                user.dateofbirth = form.dateofbirth.data
                user.ssn = form.ssn.data
                try:
                    user.set_password(form.password.data)  # pw should be hashed with some salt
                    db.session.add(user)
                    db.session.commit()
                except: # Remove if coverage < 90%
                    flash('An error occured, please try again','error')
                    return make_response(render_template('form.html', form=form, title="Modify your profile!"),500)
            else:
                flash('A user already exists with this data', 'error')
                return make_response(render_template('form.html', form=form, title="Modify your profile!"),400)

            flash('The data has been changed!', 'success')
            return redirect("/")

    return render_template('form.html', form=form, title="Modify your profile!")
