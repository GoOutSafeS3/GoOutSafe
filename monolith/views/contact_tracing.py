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
    return render_template("positives.html", positives = qry, title="Positives")


@contact_tracing.route('/positives/mark', methods=['GET','POST'])
@health_authority_required
def _mark_as_positive():
    form = SearchUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            qry = db.session.query(User)\
            .filter_by(is_admin = False)\
            .filter_by(is_health_authority=False)\
            .filter_by(rest_id = None)

            try:
                if request.form["email"] == "" and request.form["telephone"] == "" and request.form["ssn"] == "":
                    flash("Please fill in a field","warning")
                    return render_template('form.html', form=form, title="Mark a User")

                if request.form["email"] != "":
                    qry = qry.filter_by(email = request.form["email"])
                if request.form["telephone"] != "":
                    qry = qry.filter_by(phone = request.form["telephone"])
                if request.form["ssn"] != "":
                    qry = qry.filter_by(ssn = request.form["ssn"])
            except:
                flash("Bad Form","error")
                return render_template('form.html', form=form, title="Mark a User")


            qry = qry.all()

            if len(qry) == 0:
                flash("User not found","error")
                return render_template('form.html', form=form, title="Mark a User")
            elif len(qry) > 1:
                flash("More users have been found, please select only one","error")
                return render_template('positives.html', form=form, title="Mark a User", positives=qry)
            else:
                qry = qry[0]

            if mark_as_positive(qry.id):
                flash("The user was marked","success")
                return redirect("/positives")
            else: # remove if coverage <90%
                flash("User not found","error")
                return render_template('form.html', form=form, title="Mark a User")
        
    return render_template('form.html', form=form, title="Mark a User")

@contact_tracing.route('/positives/unmark', methods=['GET','POST'])
@health_authority_required
def _unmark_as_positive():
    form = SearchUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            qry = db.session.query(User)\
            .filter_by(is_admin = False)\
            .filter_by(is_health_authority=False)\
            .filter_by(rest_id = None)
            
            try:
                if request.form["email"] == "" and request.form["telephone"] == "" and request.form["ssn"] == "":
                    flash("Please fill in a field","warning")
                    return render_template('form.html', form=form, title="Unmark a User")

                if request.form["email"] != "":
                    qry = qry.filter_by(email = request.form["email"])
                if request.form["telephone"] != "":
                    qry = qry.filter_by(phone = request.form["telephone"])
                if request.form["ssn"] != "":
                    qry = qry.filter_by(ssn = request.form["ssn"])
            except:
                flash("Bad Form","error")
                return render_template('form.html', form=form, title="Unmark a User")

            qry = qry.all()

            if len(qry) == 0:
                flash("User not found","error")
                return render_template('form.html', form=form, title="Unmark a User")
            elif len(qry) > 1:
                flash("More users have been found, please select only one","error")
                return render_template('positives.html', form=form, title="Unmark a User", positives=qry)
            else:
                qry = qry[0]

            if not qry.is_positive:
                flash("The user is not positive","warning")
                return render_template('form.html', form=form, title="Unmark a User")

            if unmark_as_positive(qry.id):
                flash("The user was unmarked","success")
                return redirect("/positives")
            else: # remove if coverage <90%
                flash("User not found","error")
                return render_template('form.html', form=form, title="Unmark a User")

    return render_template('form.html', form=form, title="Unmark a User")


@contact_tracing.route('/positives/<int:pos_id>/mark', methods=['GET'])
@health_authority_required
def _mark_as_positive_by_id(pos_id):

    qry = db.session.query(User)\
        .filter_by(id = pos_id)\
        .filter_by(is_admin = False)\
        .filter_by(is_health_authority=False)\
        .filter_by(rest_id = None)\
        .first()

    if qry is None:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)

    if mark_as_positive(qry.id):
        flash("The user was marked","success")
        return redirect("/positives")
    else: # remove if coverage <90%
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)

@contact_tracing.route('/positives/<int:pos_id>/unmark', methods=['GET'])
@health_authority_required
def _unmark_as_positive_by_id(pos_id):

    qry = db.session.query(User)\
        .filter_by(id = pos_id)\
        .filter_by(is_admin = False)\
        .filter_by(is_health_authority=False)\
        .filter_by(rest_id = None)\
        .first()

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

    