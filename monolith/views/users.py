from flask import Blueprint, redirect, render_template, request, flash, make_response
from flask_login import login_required

from monolith.auth import admin_required, is_admin
from monolith.forms import UserForm, OperatorForm
from monolith.database import User, db, Restaurant

users = Blueprint('users', __name__)


@users.route('/users')
@login_required
def _users():
    if is_admin():
        users = db.session.query(User)
        return render_template("users.html", users=users)


@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            password = request.form['password']
            password_repeat = request.form['password_repeat']
            if password != password_repeat:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('create_user.html', form=form),200)

            userGet = User.query.filter_by(email=form.email.data).first()
            if userGet is None:
                new_user = User()
                new_user.firstname = form.firstname.data
                new_user.lastname = form.lastname.data
                new_user.email = form.email.data
                new_user.set_password(form.password.data)
                new_user.phone = form.telephone.data
                new_user.dateofbirth = form.dateofbirth.data
                try:
                    new_user.set_password(form.password.data)  # pw should be hashed with some salt
                    db.session.add(new_user)
                    db.session.commit()
                except: # Remove if coverage < 90%
                    flash('User not inserted','error')
                    return make_response(render_template('create_user.html', form=form),500)
            else:
                flash('Existing user', 'error')
                return make_response(render_template('create_user.html', form=form),400)

            flash('User registerd succesfully','success')
            return make_response(render_template('create_user.html',  form=form),200)

    return render_template('create_user.html', form=form)


@users.route('/create_operator', methods=['GET', 'POST'])
def create_operator():
    form = OperatorForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            password = request.form['password']
            password_repeat = request.form['password_repeat']
            if password != password_repeat:
                flash('Passwords do not match', 'warning')
                return make_response(render_template('create_operator.html', form=form),200)

            userGet = User.query.filter_by(email=form.email.data).first()
            userRestaurant = Restaurant.query.filter_by(name=form.restaurant_name.data).first()
            if userRestaurant is None:
                new_rest = Restaurant()
                new_rest.name = form.restaurant_name.data
                new_rest.lat = form.restaurant_latitude.data
                new_rest.lon = form.restaurant_longitude.data
                new_rest.phone = form.restaurant_phone.data
                if userGet is None:
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
                        return make_response(render_template('create_operator.html', form=form),500)
                else:
                    flash('Existing operator', 'error')
                    return make_response(render_template('create_operator.html', form=form), 400)
            else:
                flash('Existing restaurant', 'error')
                return make_response(render_template('create_operator.html', form=form), 400)

            flash('Operator registerd succesfully','success')
            return make_response(render_template('create_operator.html',  form=form),200)

    return render_template('create_operator.html', form=form)

