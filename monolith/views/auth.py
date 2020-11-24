from flask import Blueprint, render_template, redirect, request, flash, make_response
from flask_login import login_user, logout_user
from monolith.gateway import get_getaway
from monolith.forms import LoginForm
from werkzeug.security import check_password_hash
from monolith.auth import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user, status = get_getaway().get_users(email=request.form['email'])
            if status == 200 and user is not None:
                password = request.form['password']
                user = user[0]
                password_hash = user['password']
                checked = check_password_hash(password_hash, password)
                if checked:
                    user = User(user['id'],user['is_operator'],user['is_admin'],user['is_health_authority'], password_hash)
                    login_user(user)
                    return redirect('/')
                else:
                    flash('Wrong password', 'error')
                    return make_response(render_template('login.html', form=form), 401)
            flash('Wrong email', 'error')
            return make_response(render_template('login.html', form=form), 401)
        flash('Bad form', 'error')
        return make_response(render_template('login.html', form=form), 400)
    return make_response(render_template('login.html', form=form), 200)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')
