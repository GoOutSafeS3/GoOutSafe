from flask import Blueprint, redirect, render_template, request, flash, make_response
from monolith.auth import health_authority_required
from monolith.forms import SearchUserForm
import datetime
from datetime import timedelta, datetime
from monolith.gateway import get_getaway

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
    positives, status = get_getaway().get_positive_users()
    if positives is None or status != 200:
        return make_response(render_template("error.html", error = status), status)
    return render_template("positives.html", positives = positives, title="Positives")


@contact_tracing.route('/positives/contacts', methods=['GET','POST'])
@health_authority_required
def _contacts():
    """ Allows you to search, given the identifiers of a user (email, telephone and ssn (if available)), the contacts of a positive user """
    form = SearchUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                if request.form["email"] == "" and request.form["telephone"] == "" and request.form["ssn"] == "":
                    flash("Please fill in a field","warning")
                    return render_template('form.html', form=form, title="Find Contacts")
                if request.form["email"] != "":
                    email_param = request.form['email']
                else:
                    email_param = None
                if request.form["telephone"] != "":
                    phone_param = request.form['telephone']
                else:
                    phone_param = None
                if request.form["ssn"] != "":
                    ssn_param = request.form['ssn']
                else:
                    ssn_param = None
                users, status = get_getaway().get_users(email=email_param,phone=phone_param, ssn=ssn_param)
            except:
                flash("Bad Form","error")
                return render_template('form.html', form=form, title="Find Contacts")

            if users is None or status != 200:
                return make_response(render_template('error.html', error = status), status)

            if len(users) == 0:
                flash("User not found","error")
                return render_template('form.html', form=form, title="Find Contacts")
            elif len(users) > 1:
                flash("More users have been found, please try again","error")
                return render_template('form.html', form=form, title="Find Contacts")
            else:
                user = users[0]

            if user['is_positive']:
                return redirect(f"/positives/{user['id']}/contacts")
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
            try:
                if request.form["email"] == "" and request.form["telephone"] == "" and request.form["ssn"] == "":
                    flash("Please fill in a field","warning")
                    return render_template('mark_positives.html', form=form, title="Mark a User")
                if request.form["email"] != "":
                    email_param = request.form['email']
                else:
                    email_param = None
                if request.form["telephone"] != "":
                    phone_param = request.form['telephone']
                else:
                    phone_param = None
                if request.form["ssn"] != "":
                    ssn_param = request.form['ssn']
                else:
                    ssn_param = None
                users, status = get_getaway().get_users(email=email_param,phone=phone_param, ssn=ssn_param)
            except:
                flash("Bad Form","error")
                return render_template('mark_positives.html', form=form, title="Mark a User")

            if users is None or status != 200:
                return make_response(render_template('error.html', error = status), status)

            if len(users) == 0:
                flash("User not found","error")
                return render_template('mark_positives.html', form=form, title="Mark a User")
            elif len(users) > 1:
                flash("More users have been found, please try again","error")
                return render_template('mark_positives.html', form=form, title="Mark a User")
            else:
                user = users[0]

            result, status = get_getaway().mark_user(user['id'])

            if result is not None and status == 200:
                flash("The user was marked","success")
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
            try:
                if request.form["email"] == "" and request.form["telephone"] == "" and request.form["ssn"] == "":
                    flash("Please fill in a field","warning")
                    return render_template('form.html', form=form, title="Unmark a User")
                if request.form["email"] != "":
                    email_param = request.form['email']
                else:
                    email_param = None
                if request.form["telephone"] != "":
                    phone_param = request.form['telephone']
                else:
                    phone_param = None
                if request.form["ssn"] != "":
                    ssn_param = request.form['ssn']
                else:
                    ssn_param = None
                users, status = get_getaway().get_users(email=email_param,phone=phone_param, ssn=ssn_param)
            except:
                flash("Bad Form","error")
                return render_template('mark_positives.html', form=form, title="Mark a User")

            if users is None or status != 200:
                return make_response(render_template('error.html', error = status), status)

            if len(users) == 0:
                flash("User not found","error")
                return render_template('form.html', form=form, title="Unmark a User")
            elif len(users) > 1:
                flash("More users have been found, please try again","error")
                return render_template('form.html', form=form, title="Unmark a User")
            else:
                user = users[0]

            if not user['is_positive']:
                flash("The user is not positive","warning")
                return render_template('form.html', form=form, title="Unmark a User")

            result, status = get_getaway().unmark_user(user['id'])

            if result is not None and status == 200:
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
    user, status = get_getaway().mark_user(pos_id)

    if status == 404:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)
    elif user is None or status != 200:
        return make_response(render_template("error.html", error = status), status)

    return redirect("/positives")


@contact_tracing.route('/positives/<int:pos_id>/unmark', methods=['GET'])
@health_authority_required
def _unmark_as_positive_by_id(pos_id):
    """ Allows you to mark as negative a positive user given his or her id 
    Useful when embedding functionality in a button

    Error status codes:
        404 -- User not found or user not positive
    """
    user, status = get_getaway().unmark_user(pos_id)

    if status == 404:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)
    elif user is None or status != 200:
        return make_response(render_template("error.html", error = status), status)

    return redirect("/positives")


@contact_tracing.route('/positives/<int:user_id>/contacts')
@health_authority_required
def user_contacts(user_id):
    """ Allows you to search, given the id the contacts of a positive user 

    Error status codes:
        404 -- User not found or user not positive
    """
    user, status = get_getaway().get_user(user_id)
    if user is None or status != 200:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)

    if not user.is_positive:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)

    users, status = get_getaway().get_user_contacts(user_id,
        begin=str(datetime.today() - timedelta(days=14)),
        end=str(datetime.today()))

    if status == 404:
        flash("User not found","error")
        return make_response(render_template('error.html', error='404'), 404)
    elif status != 200:
        return make_response(render_template('error.html', error=status), status)
        
    return render_template("users.html", users=users)