from flask import Blueprint, render_template, redirect, request, flash, make_response
from flask_login import (current_user, login_user, logout_user,
                         login_required)

from monolith.database import db, User
from monolith.forms import LoginForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email, password = form.data['email'], form.data['password']
            q = db.session.query(User).filter(User.email == email)
            user = q.first()
            if user is not None:
                print(q.first().id)
            if user is not None and user.authenticate(password):
                login_user(user)
                return redirect('/')
            flash('Wrong email or password','error')
            return make_response(render_template('login.html', form=form), 401)
        flash('Bad form','error')
        return make_response(render_template('login.html', form=form), 400)
    return make_response(render_template('login.html', form=form), 200)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')
