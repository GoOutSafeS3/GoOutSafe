from flask import Blueprint, render_template, redirect, request, flash, make_response
from flask_login import login_user, logout_user
from monolith.gateway import gateway
from monolith.forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user, status = gateway.login_user(request.form)
            if status == 200 and user is not None:
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
