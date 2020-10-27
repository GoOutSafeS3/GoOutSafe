from flask import Blueprint, redirect, render_template, request, flash, make_response
from flask_login import login_required

from monolith.auth import admin_required, is_admin, health_auyhority_required
from monolith.forms import UserForm, OperatorForm
from monolith.database import User, db, Restaurant

import datetime

contact_tracing = Blueprint('contact_tracing', __name__)


@contact_tracing.route('/positives', methods=['GET'])
@health_auyhority_required
def positives():
    qry = db.session.query(User).filter_by(is_positive = True).all()
    return render_template("positives.html", positives = qry)

@contact_tracing.route('/positives/<user_id>', methods=['GET','POST'])
@health_auyhority_required
def mark_as_positive(user_id):
    qry = db.session.query(User).filter_by(id = user_id).all()
    if qry == []:
        return make_response(render_template('error.html', error='404'),404)
    else:
        qry = qry[0]
        qry.is_positive = True
        qry.positive_datetime = datetime.datetime.now()
        db.session.commit()
        flash("The user was marked as positive","success")
        return redirect("/")