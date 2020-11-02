from flask import Blueprint, redirect, render_template, request, flash, make_response
from flask_login import login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from monolith.forms import EditUserForm
from monolith.database import User, db, Restaurant, Booking
from datetime import timedelta, datetime
from flask_login import login_required

editprofile = Blueprint('editprofile', __name__)


@editprofile.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit():

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