from flask import Blueprint, redirect, render_template, request, flash, make_response, current_app
from flask_login import login_required

from monolith.auth import admin_required, is_admin, health_auyhority_required
from monolith.forms import UserForm, OperatorForm, SearchUserForm
from monolith.database import User, db, Restaurant
from monolith.utilities.contact_tracing import mark_as_positive, unmark_as_positive

import datetime

contact_tracing = Blueprint('contact_tracing', __name__)

@contact_tracing.route('/positives', methods=['GET'])
@health_auyhority_required
def positives():
    qry = db.session.query(User).filter_by(is_positive = True).all()
    return render_template("positives.html", positives = qry)

@contact_tracing.route('/positives/mark', methods=['GET','POST'])
@health_auyhority_required
def _mark_as_positive():
    form = SearchUserForm()
    if request.method == 'POST':
        qry = db.session.query(User).filter_by(email = request.form["email"]).all()[0]
        if qry == []:
            flash("User not found","error")
            return redirect("/positives/mark",code=404)

        if mark_as_positive(qry.id):
            flash("The user was marked","success")
            return redirect("/positives/mark")
        else:
            flash("User not found","error")
            return redirect("/positives/mark",code=404)
    
    return render_template('form.html', form=form, title="Mark a User")

@contact_tracing.route('/positives/unmark', methods=['GET','POST'])
@health_auyhority_required
def _unmark_as_positive():
    form = SearchUserForm()
    if request.method == 'POST':
        qry = db.session.query(User).filter_by(email = request.form["email"]).all()[0]
        if qry == []:
            flash("User not found","error")
            return redirect("/positives/unmark",code=404)

        if unmark_as_positive(qry.id):
            flash("The user was unmarked","success")
            return redirect("/positives/unmark")
        else:
            flash("User not found","error")
            return redirect("/positives/unmark",code=404)
    
    return render_template('form.html', form=form, title="Unmark a User")