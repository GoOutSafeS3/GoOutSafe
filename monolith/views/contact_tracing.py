from flask import Blueprint, redirect, render_template, request, flash, make_response, current_app
from flask_login import login_required

from monolith.auth import admin_required, is_admin, health_authority_required
from monolith.forms import UserForm, OperatorForm, SearchUserForm
from monolith.database import User, db, Restaurant
from monolith.utilities.contact_tracing import mark_as_positive, unmark_as_positive

import datetime

contact_tracing = Blueprint('contact_tracing', __name__)


@contact_tracing.route('/positives', methods=['GET'])
@health_authority_required
def positives():
    qry = db.session.query(User).filter_by(is_positive = True).all()
    return render_template("positives.html", positives = qry)


@contact_tracing.route('/positives/mark', methods=['GET','POST'])
@health_authority_required
def _mark_as_positive():
    form = SearchUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            qry = db.session.query(User).filter_by(email = request.form["email"]).first()
            if qry is None:
                flash("User not found","error")
                return make_response(render_template('error.html', error='404'), 404)

            now = datetime.datetime.now()
            day, month, year = (int(x) for x in request.form["dateofbirth"].split('/'))   
            dateofbirth = now.replace(year=year,month=month,day=day,hour=0,minute=0,second=0,microsecond=0)

            if qry.firstname == request.form["firstname"] and qry.lastname == request.form["lastname"] and qry.dateofbirth == dateofbirth:
                if mark_as_positive(qry.id):
                    flash("The user was marked","success")
                    return redirect("/positives/mark")
                else: # remove if coverage <90%
                    flash("User not found","error")
                    return make_response(render_template('error.html', error='404'), 404)
            else:
                flash("Bad Form","error")
        
    return render_template('form.html', form=form, title="Mark a User")

@contact_tracing.route('/positives/unmark', methods=['GET','POST'])
@health_authority_required
def _unmark_as_positive():
    form = SearchUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            qry = db.session.query(User).filter_by(email = request.form["email"]).first()
            if qry is None:
                flash("User not found","error")
                return make_response(render_template('error.html', error='404'), 404)
            else:
                now = datetime.datetime.now()
                day, month, year = (int(x) for x in request.form["dateofbirth"].split('/'))   
                dateofbirth = now.replace(year=year,month=month,day=day,hour=0,minute=0,second=0,microsecond=0)

                if qry.firstname == request.form["firstname"] and qry.lastname == request.form["lastname"] and qry.dateofbirth == dateofbirth:
                        return redirect(f"/positives/{qry.get_id()}/unmark")
                else:
                    flash("Bad Form","error")

    return render_template('form.html', form=form, title="Unmark a User")


@contact_tracing.route('/positives/<int:pos_id>/unmark', methods=['GET'])
@health_authority_required
def _unmark_as_positive_by_id(pos_id):

    qry = db.session.query(User).filter_by(id = pos_id).first()
    if qry is None:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)

    if not qry.is_positive:
        flash("The user is not positive","warning")
        return make_response(render_template('error.html', error='404'), 404)

    if unmark_as_positive(qry.id):
        flash("The user was unmarked","success")
        return redirect("/positives")
    else: # remove if coverage <90%
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)

    