from flask import Blueprint, redirect, render_template, request, flash, make_response, current_app
from flask_login import login_required
from monolith.auth import admin_required, is_admin, health_authority_required
from monolith.forms import UserForm, OperatorForm, SearchUserForm
from monolith.database import User, db, Restaurant, Notification
from monolith.utilities.contact_tracing import mark_as_positive, unmark_as_positive, get_user_contacts, get_operators_contacts
import datetime
from datetime import timedelta, datetime
from monolith.utilities.notification import add_notification, add_bookings_notifications

contact_tracing = Blueprint('contact_tracing', __name__)

"""
All features are only available to the health authority

Error status codes:
    401 -- The user is not the health authority
"""


@contact_tracing.route('/positives', methods=['GET'])
@health_authority_required
def positives():
    """ Allows you to view the list of currently positive users """
    qry = db.session.query(User).filter_by(is_positive = True).all()
    return render_template("positives.html", positives = qry, title="Positives")


@contact_tracing.route('/positives/contacts', methods=['GET','POST'])
@health_authority_required
def _contacts():
    """ Allows you to search, given the identifiers of a user (email, telephone and ssn (if available)), the contacts of a positive user """
    form = SearchUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            qry = db.session.query(User)\
            .filter_by(is_admin = False)\
            .filter_by(is_health_authority=False)\
            .filter_by(rest_id = None) # not an operator

            try:
                if request.form["email"] == "" and request.form["telephone"] == "" and request.form["ssn"] == "":
                    flash("Please fill in a field","warning")
                    return render_template('form.html', form=form, title="Find Contacts")

                if request.form["email"] != "":
                    qry = qry.filter_by(email = request.form["email"])
                if request.form["telephone"] != "":
                    qry = qry.filter_by(phone = request.form["telephone"])
                if request.form["ssn"] != "":
                    qry = qry.filter_by(ssn = request.form["ssn"])
            except:
                flash("Bad Form","error")
                return render_template('form.html', form=form, title="Find Contacts")


            qry = qry.all()

            if len(qry) == 0:
                flash("User not found","error")
                return render_template('form.html', form=form, title="Find Contacts")
            elif len(qry) > 1:
                flash("More users have been found, please try again","error")
                return render_template('form.html', form=form, title="Find Contacts")
            else:
                qry = qry[0]

            if qry.is_positive:
                return redirect(f"/positives/{qry.id}/contacts")
            else:
                flash("The user is not positive","error")
                
    return render_template('form.html', form=form, title="Find Contacts")


@contact_tracing.route('/positives/mark', methods=['GET','POST'])
@health_authority_required
def _mark_as_positive():
    """ Allows you to mark as positive a user given his or her identifiers of a user (email, telephone and ssn (if available)) 
    A positive user can be marked positive again
    Notifications are sent to all his contacts (other customers or operators)

    And to the operators who have received your booking
    """
    form = SearchUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            qry = db.session.query(User)\
            .filter_by(is_admin = False)\
            .filter_by(is_health_authority=False)\
            .filter_by(rest_id = None) # not an operator

            try:
                if request.form["email"] == "" and request.form["telephone"] == "" and request.form["ssn"] == "":
                    flash("Please fill in a field","warning")
                    return render_template('mark_positives.html', form=form, title="Mark a User")

                if request.form["email"] != "":
                    qry = qry.filter_by(email = request.form["email"])
                if request.form["telephone"] != "":
                    qry = qry.filter_by(phone = request.form["telephone"])
                if request.form["ssn"] != "":
                    qry = qry.filter_by(ssn = request.form["ssn"])
            except:
                flash("Bad Form","error")
                return render_template('mark_positives.html', form=form, title="Mark a User")

            qry = qry.all()

            if len(qry) == 0:
                flash("User not found","error")
                return render_template('mark_positives.html', form=form, title="Mark a User")
            elif len(qry) > 1:
                flash("More users have been found, please try again","error")
                return render_template('mark_positives.html', form=form, title="Mark a User")
            else:
                qry = qry[0]

            if mark_as_positive(qry.id):
                flash("The user was marked","success")
                two_weeks = timedelta(days=14)
                today = datetime.today()
                date_start = today - two_weeks
                users_to_be_notified = get_user_contacts(qry.id, date_start, today)
                operators_to_be_notified = get_operators_contacts(qry.id, date_start, today)
                for user in users_to_be_notified:
                    add_notification(qry.id, user.id, 0) # notifications to other customers 
                for operator in operators_to_be_notified:
                    add_notification(qry.id, operator.id, 1) # notifications to operators
                add_bookings_notifications(qry.id) # notifications for his/her bookings
                return redirect("/positives")
            else:
                flash("User not found","error")
                return render_template('mark_positives.html', form=form, title="Mark a User")
        
    return render_template('mark_positives.html', form=form, title="Mark a User")


@contact_tracing.route('/positives/unmark', methods=['GET','POST'])
@health_authority_required
def _unmark_as_positive():
    """ Allows you to mark as negative a positive user given his or her identifiers of a user (email, telephone and ssn (if available)) """
    form = SearchUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            qry = db.session.query(User)\
            .filter_by(is_admin = False)\
            .filter_by(is_health_authority=False)\
            .filter_by(rest_id = None) # not an operator
            
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
                flash("More users have been found, please try again","error")
                return render_template('form.html', form=form, title="Unmark a User")
            else:
                qry = qry[0]

            if not qry.is_positive:
                flash("The user is not positive","warning")
                return render_template('form.html', form=form, title="Unmark a User")

            if unmark_as_positive(qry.id):
                flash("The user was unmarked","success")
                return redirect("/positives")
            else:
                flash("User not found","error")
                return render_template('form.html', form=form, title="Unmark a User")

    return render_template('form.html', form=form, title="Unmark a User")


@contact_tracing.route('/positives/<int:pos_id>/mark', methods=['GET'])
@health_authority_required
def _mark_as_positive_by_id(pos_id):
    """ Allows you to mark as positive a user given his or her id 
    A positive user can be marked positive again
    Useful when embedding functionality in a button

    Notifications are sent to all his contacts (other customers or operators)
    And to the operators who have received your booking

    Error status codes:
        404 -- User not found
    """
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
        two_weeks = timedelta(days=14)
        today = datetime.today()
        date_start = today - two_weeks
        users_to_be_notificated = get_user_contacts(qry.id, date_start, today)
        for user in users_to_be_notificated:
            add_notification(qry.id, user.id, 0)
        operators_to_be_notified = get_operators_contacts(qry.id, date_start, today)
        for operator in operators_to_be_notified:
            add_notification(qry.id, operator.id, 1)
        add_bookings_notifications(qry.id)
        return redirect("/positives")
    else:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)


@contact_tracing.route('/positives/<int:pos_id>/unmark', methods=['GET'])
@health_authority_required
def _unmark_as_positive_by_id(pos_id):
    """ Allows you to mark as negative a positive user given his or her id 
    Useful when embedding functionality in a button

    Error status codes:
        404 -- User not found or user not positive
    """
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
    else:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)


@contact_tracing.route('/positives/<int:user_id>/contacts')
@health_authority_required
def user_contacts(user_id):
    """ Allows you to search, given the id the contacts of a positive user 

    Error status codes:
        404 -- User not found or user not positive
    """
    qry = db.session.query(User)\
        .filter_by(id = user_id)\
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
        
    return render_template("users.html",
        users=get_user_contacts(user_id, datetime.today() - timedelta(days=14), datetime.today()))