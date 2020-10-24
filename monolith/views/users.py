from flask import Blueprint, redirect, render_template, request, flash, make_response
from monolith.auth import admin_required
from monolith.forms import UserForm, OperatorForm
from monolith.database import User, db

users = Blueprint('users', __name__)


@users.route('/users')
def _users():
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
                form.populate_obj(new_user)
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
            return make_response(_users(),200)

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
            if userGet is None:
                new_user = User()
                form.populate_obj(new_user)
                try:
                    new_user.set_password(form.password.data)  # pw should be hashed with some salt
                    db.session.add(new_user)
                    db.session.commit()
                except: # Remove if coverage < 90%
                    flash('Operator not inserted','error')
                    return make_response(render_template('create_operator.html', form=form),500)
            else:
                flash('Existing operator', 'error')
                return make_response(render_template('create_operator.html', form=form),400)

            flash('Operator registerd succesfully','success')
            return make_response(_users(),200)

    return render_template('create_operator.html', form=form)

