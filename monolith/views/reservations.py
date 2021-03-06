from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.auth import current_user, operator_required
from flask_login import current_user, login_required
from monolith.forms import BookingForm, BookingList
from monolith.gateway import get_getaway
import datetime
import dateutil.parser

reservations = Blueprint('reservations', __name__)


@reservations.route('/restaurants/<int:restaurant_id>/book', methods=['GET', 'POST'])
@login_required
def _book(restaurant_id):
    """ It allows you to book in a specific restaurant

    Error status code:
        400 -- The form is filled in incorrectly or it is not possible to make a reservation with that data
        401 -- The user cannot make the reservation (it is positive, he is not a customer, he is not logged in)
        404 -- The restaurant does not exist
        409 -- Impossible to make the reservation
        500 -- An error occured
    """
    form = BookingForm()

    rest,code = get_getaway().get_restaurant(restaurant_id)
    if code is not None and code == 404:
        flash("Restaurant not found!","error")
        return make_response(render_template('error.html', error='404'),404)
    elif code is None or code != 200 or rest is None or rest == {}:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template('form.html', form=form, title="View reservations"),500)

    if current_user.is_admin  or current_user.is_operator  or current_user.is_health_authority :
        flash("Please log as customer to book a table","error")
        return make_response(render_template('error.html', error="401"), 401)

    if current_user.is_positive:
        flash("You cannot book as long as you are positive","error")
        return make_response(render_template('error.html', error="401"), 401)

    if request.method == 'POST':
        if form.validate_on_submit():
            number_of_people = request.form["number_of_people"]
            booking_date = request.form["booking_date"]
            booking_hr = request.form["booking_hr"]
            booking_min = request.form["booking_min"]

            now = datetime.datetime.now() + datetime.timedelta(hours=1) # timezone aware
            day, month, year = (int(x) for x in booking_date.split('/'))   
            booking_datetime = now.replace(year=year,month=month,day=day,hour=int(booking_hr),minute=int(booking_min),second=0,microsecond=0)
            
            if booking_datetime < now:
                flash("You cannot book before now","error")
                return make_response(render_template('form.html', form=form, title = "Book a table!"),400)

            booking, code = get_getaway().new_booking(user_id=current_user.id ,rest_id=restaurant_id,number_of_people=int(number_of_people),booking_datetime=booking_datetime.isoformat())
            
            if booking is None or code is None:
                flash("Sorry, an error occured. Please, try again.","error")
                return make_response(render_template('form.html', form=form, title="View reservations"),500)
            elif code == 201:
                flash("The booking was confirmed","success")
                return redirect(f"/restaurants/{restaurant_id}")
            elif code == 400:
                flash("Bad Request","warning")
                return make_response(render_template('form.html', form=form, title="View reservations"),400)
            elif code  == 404:
                flash("Booking not found!","error")
                return make_response(render_template('error.html', error='404'),404)
            elif code == 409:
                flash(booking["detail"],"warning")
                return make_response(render_template('form.html', form=form, title="View reservations"),400)
            else:
                flash("Sorry, an error occured. Please, try again.","error")
                return make_response(render_template('form.html', form=form, title="View reservations"),500)

    return render_template('form.html', form=form, title = "Book a table!")


@reservations.route('/restaurants/<int:restaurant_id>/reservations', methods=['GET', 'POST'])
@operator_required
def _booking_list(restaurant_id):
    """ It allows the current operator to view all bookings in a given period of time

    Error status code:
        400 -- The form is filled in incorrectly
        401 -- The user is not the restaurant operator
        404 -- The restaurant does not exist
        500 -- An error occured
    """

    form = BookingList()

    rest,code = get_getaway().get_restaurant(restaurant_id)
    if code is not None and code == 404:
        flash("Restaurant not found!","error")
        return make_response(render_template('error.html', error='404'),404)
    elif code is None or code != 200 or rest is None or rest == {}:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template('form.html', form=form, title="View reservations"),500)

    if current_user.rest_id  != restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    if request.method == 'POST':
        if form.validate_on_submit():
            now = datetime.datetime.now()
        
            from_date = request.form["from_date"]
            from_hr = request.form["from_hr"]
            from_min = request.form["from_min"]
            from_day, from_month, from_year = (int(x) for x in from_date.split('/'))   
            from_datetime = now.replace(year=from_year,month=from_month,day=from_day,hour=int(from_hr),minute=int(from_min),second=0,microsecond=0)

            to_date = request.form["to_date"]
            to_hr = request.form["to_hr"]
            to_min = request.form["to_min"]
            to_day, to_month, to_year = (int(x) for x in to_date.split('/'))   
            to_datetime = now.replace(year=to_year,month=to_month,day=to_day,hour=int(to_hr),minute=int(to_min),second=0,microsecond=0)

            if from_datetime >= to_datetime:
                flash("Invalid time interval","error")
                return make_response(render_template('form.html', form=form, title="View reservations"),400)


            qry,status_code = get_getaway().get_bookings(rest=restaurant_id, begin=from_datetime.isoformat(), end=to_datetime.isoformat(),with_user=True)
            
            if status_code is None or status_code != 200:
                flash("Sorry, an error occured. Please, try again.","error")
                return make_response(render_template('form.html', form=form, title="View reservations"),500)
            elif qry is None or qry==[]:
                qry = []
                flash("No reservations were found","warning")

            return make_response(render_template("reservations.html", reservations=qry, title="View reservations"),200)

    return make_response(render_template('form.html', form=form, title="View reservations"),200)



@reservations.route('/restaurants/<int:restaurant_id>/reservations/today', methods=['GET'])
@operator_required
def _today_booking_list(restaurant_id):
    """ It allows the current operator to view all bookings of today

    Error status code:
        401 -- The user is not the restaurant operator
        404 -- The restaurant does not exist
        500 -- An error occured
    """
    rest,code = get_getaway().get_restaurant(restaurant_id)
    if code is not None and code == 404:
        flash("Restaurant not found!","error")
        return make_response(render_template('error.html', error='404'),404)
    elif code is None or code != 200 or rest is None or rest == {}:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template("reservations.html", reservations=[], title="Today's Reservations"),500)

    if current_user.rest_id  != restaurant_id:
        return make_response(render_template('error.html', error='401'), 401)
    
    today = datetime.datetime.now()

    from_datetime = today.replace(hour=0,minute=0,second=0,microsecond=0)
    to_datetime = today.replace(hour=23,minute=59,second=59,microsecond=999999)

    qry,status_code = get_getaway().get_bookings(rest=restaurant_id, begin=from_datetime.isoformat(), end=to_datetime.isoformat(),with_user=True)
            
    if status_code is None or status_code != 200:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template("reservations.html", reservations=[], title="Today's Reservations"),500)
    elif qry is None:
        qry = []
        flash("No reservations were found","warning")

    return make_response(render_template("reservations.html", reservations=qry, title="Today's Reservations"),200)


@reservations.route('/reservations/<int:reservation_id>/entrance', methods=['GET', 'POST'])
@operator_required
def _register_entrance(reservation_id):
    """ It allows the operator ro register the entrance of the users into the restaurant (Given a reservation)

    Error status code:
        401 -- The user is not the restaurant operator
        404 -- The reservation does not exist
        409 -- Impossible to set the entrance
        500 -- An error occured
    """

    booking, code = get_getaway().get_a_booking(id=reservation_id)
    
    if booking is None or code != 200:
        return make_response(render_template('error.html', error=code),code)
    if booking['restaurant_id'] != current_user.rest_id:
        return make_response(render_template('error.html', error='401'),401)

    _, code = get_getaway().edit_booking(booking_id=reservation_id,entrance=True)

    if code is not None and code == 200:
        flash("Entrance registered!","success")
    elif code is not None and code == 404:
        flash("Booking not found!","error")
        return make_response(render_template('error.html', error='404'),404)
    elif code is not None and code == 409 or code == 400:
        flash("Impossible to edit the requested booking","warning")
    else:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template("reservations.html", reservations=[], title="Today's Reservations"),500)
    

    return redirect(f"/reservations/{reservation_id}")

@reservations.route('/reservations/<int:reservation_id>', methods=['GET'])
@operator_required
def _reservation(reservation_id):
    """ It allows the restaurant operator to view the details of a reservation

    Error status code:
        401 -- The user is not the restaurant operator
        404 -- The reservation does not exist
        500 -- An error occured
    """


    booking, status = get_getaway().get_a_booking(id=reservation_id,with_user=True)

    if  status is None or status != 200 or booking is None or booking == {}:
        return make_response(render_template('error.html', error=status), status)
    elif booking['restaurant_id'] != current_user.rest_id :
        return make_response(render_template('error.html', error='401'),401)
    
    return render_template("reservation.html", reservation=booking)


@reservations.route('/reservations/<int:reservation_id>/delete', methods=['GET', 'DELETE', 'POST'])
@login_required
def _reservation_delete(reservation_id):
    """ It allows the restaurant operator or the user that made the reservation to delete the reservation

    Error status code:
        401 -- The user is not the restaurant operator or the user that made the reservation
        403 -- Impossible to delete the reservation
        404 -- The reservation does not exist
    """

    booking, status = get_getaway().get_a_booking(id=reservation_id)
    
    if status == 404:
        flash("Booking not found!","error")
        return make_response(render_template('error.html', error='404'),404)
    if booking is None or status is None or status != 200:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template("index.html"),500)
        
    if booking['restaurant_id'] != current_user.rest_id and booking['user_id'] != current_user.id:
        return make_response(render_template('error.html', error='401'),401)

    _, code = get_getaway().delete_booking(id=reservation_id)

    if code is not None and code == 204:
        flash("Booking deleted!","success")
    elif code is not None and code == 404:
        flash("Booking not found!","error")
        return make_response(render_template('error.html', error='404'),404)
    elif code is not None and code == 403:
        flash("Impossible to delete the requested booking","warning")
    else:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template("index.html"),500)
    

    return redirect("/")


@reservations.route('/reservations/<int:reservation_id>/edit', methods=['GET', 'POST'])
@login_required
def _reservation_edit(reservation_id):
    """ It allows the restaurant operator or the user that made the reservation to edit the reservation

    Error status code:
        401 -- The user is not the restaurant operator or the user that made the reservation
        404 -- The reservation does not exist
    """

    booking, status = get_getaway().get_a_booking(id=reservation_id)

    if status == 404:
        flash("Booking not found!","error")
        return make_response(render_template('error.html', error='404'),404)
    
    if booking is None or status is None or status != 200:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template("index.html"),500)

    if booking['restaurant_id'] != current_user.rest_id and booking['user_id'] != current_user.id:
        return make_response(render_template('error.html', error='401'),401)

    if current_user.is_positive:
        flash("You cannot book as long as you are positive","error")
        return make_response(render_template('error.html', error="401"), 401)
            

    old_booking_datetime = dateutil.parser.parse(booking["booking_datetime"])
    timezone = old_booking_datetime.tzinfo
    now = datetime.datetime.now(timezone) + datetime.timedelta(hours=1) #timezone aware computation

    if old_booking_datetime <= now:
        flash("The reservation has expired","error")
        return make_response(render_template('error.html', error='404'), 404)

    restaurant_id = booking["restaurant_id"]

    form = BookingForm()
    obj = {}
    if request.method == 'POST':
        if form.validate_on_submit():
            number_of_people = request.form["number_of_people"]
            booking_date = request.form["booking_date"]
            booking_hr = request.form["booking_hr"]
            booking_min = request.form["booking_min"]

            day, month, year = (int(x) for x in booking_date.split('/'))   
            booking_datetime = now.replace(year=year,month=month,day=day,hour=int(booking_hr),minute=int(booking_min),second=0,microsecond=0)
            
            if booking_datetime < now:
                flash("You cannot book before now","error")
                return make_response(render_template('form.html', form=form, title = "Edit your booking"),400)

            booking,code = get_getaway().edit_booking(booking_id=reservation_id,number_of_people=int(number_of_people),booking_datetime=booking_datetime.isoformat())
            
            if booking is None or code is None:
                flash("Sorry, an error occured. Please, try again.","error")
                return make_response(render_template('form.html', form=form, title="View reservations"),500)
            elif code == 200:
                flash("The booking was edited!","success")
                return redirect(f"/restaurants/{restaurant_id}")
            elif code == 400:
                flash("Bad Request","warning")
                return make_response(render_template('form.html', form=form, title="View reservations"),400)
            elif status == 404:
                flash("Booking not found!","error")
                return make_response(render_template('error.html', error='404'),404)
            elif code == 409:
                flash(booking["detail"],"warning")
                return make_response(render_template('form.html', form=form, title="View reservations"),400)
            else:
                flash("Sorry, an error occured. Please, try again.","error")
                return make_response(render_template('form.html', form=form, title="View reservations"),500)
    elif request.method == "GET":
        obj["number_of_people"] = booking["number_of_people"]
        obj["booking_date"] = old_booking_datetime.strftime('%d/%m/%Y')
        obj["booking_hr"] = int(old_booking_datetime.strftime('%H'))
        obj["booking_min"] = int((int(old_booking_datetime.strftime('%M'))/15))*15 #round to a multiple of 15
        
    return render_template('edit-form.html', form=form, edited=obj, title = "Edit your booking")