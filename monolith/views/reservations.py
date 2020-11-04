from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.database import db, Restaurant, Booking, User, Table
from monolith.auth import admin_required, current_user, is_admin, operator_required
from flask_login import current_user, login_user, logout_user, login_required
from monolith.forms import UserForm, BookingForm, BookingList
from monolith.utilities.reservations import try_to_book, try_to_update
import datetime

reservations = Blueprint('reservations', __name__)


@reservations.route('/restaurants/<int:restaurant_id>/book', methods=['GET', 'POST'])
@login_required
def _book(restaurant_id):
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).first()

    if record is None:
        return make_response(render_template('error.html', error='404'), 404)

    if current_user.is_admin or current_user.is_operator or current_user.is_health_authority:
        return make_response(render_template('error.html', error="Please log as customer to book a table"), 401)

    if current_user.is_positive:
        return make_response(render_template('error.html', error="You cannot book as long as you are positive"), 401)

    form = BookingForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            number_of_people = request.form["number_of_people"]
            booking_date = request.form["booking_date"]
            booking_hr = request.form["booking_hr"]
            booking_min = request.form["booking_min"]

            now = datetime.datetime.now()
            day, month, year = (int(x) for x in booking_date.split('/'))   
            booking_datetime = now.replace(year=year,month=month,day=day,hour=int(booking_hr),minute=int(booking_min),second=0,microsecond=0)
            
            if booking_datetime < now:
                flash("You cannot book before now","error")
                return make_response(render_template('form.html', form=form, title = "Book a table!"),400)

            if try_to_book(restaurant_id, int(number_of_people), booking_datetime):
                flash("The booking was confirmed","success")
                return redirect(f"/restaurants/{restaurant_id}")
            else:
                flash("The reservation could not be made","error")
                return make_response(render_template('form.html', form=form, title = "Book a table!"),400)

    return render_template('form.html', form=form, title = "Book a table!")


@reservations.route('/restaurants/<int:restaurant_id>/reservations', methods=['GET', 'POST'])
@operator_required
def _booking_list(restaurant_id):
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).first()
    if record is None:
        return make_response(render_template('error.html', error='404'),404)

    if current_user.rest_id != restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    form = BookingList()
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

            qry = db.session.query(Booking,User)\
                            .filter_by(rest_id = current_user.get_rest_id())\
                            .filter(User.id == Booking.user_id)\
                            .filter(from_datetime <= Booking.booking_datetime)\
                            .filter(Booking.booking_datetime <= to_datetime )\
                            .all()

            return make_response(render_template("reservations.html", reservations=qry, title="View reservations"),200)

    return make_response(render_template('form.html', form=form, title="View reservations"),200)



@reservations.route('/restaurants/<int:restaurant_id>/reservations/today', methods=['GET'])
@operator_required
def _today_booking_list(restaurant_id):
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).first()
    if record is None:
        return make_response(render_template('error.html', error='404'),404)

    if current_user.rest_id != restaurant_id:
        return make_response(render_template('error.html', error='401'), 401)
    
    today = datetime.datetime.today().date()

    qry = db.session.query(Booking,User)\
                    .filter_by(rest_id = current_user.get_rest_id())\
                    .filter(User.id == Booking.user_id)\
                    .all()

    res = []
    for r in qry:
        if r.Booking.booking_datetime.date() == today:
            res.append(r)

    return make_response(render_template("reservations.html", reservations=res, title="Today's Reservations"),200)


@reservations.route('/reservations/<int:reservation_id>/entrance', methods=['GET', 'POST'])
@operator_required
def _register_entrance(reservation_id):
    
    qry = db.session.query(Booking).filter_by(id = reservation_id).first()
    
    if qry is None:
        return make_response(render_template('error.html', error='404'),404)

    if qry.rest_id != current_user.get_rest_id():
        return make_response(render_template('error.html', error='401'),401)
    
    if qry.entrance_datetime is None:
        try:
            qry.entrance_datetime = datetime.datetime.now()
            db.session.add(qry)
            db.session.commit()
            return redirect(f"/reservations/{reservation_id}")
        except: # Remove if coverage < 90%
            flash('An error occured, please try again','error')
            return redirect(f"/reservations/{reservation_id}")
    else:
        flash('The entrance of this reservation has already been registered',"error")
        return redirect(f"/reservations/{reservation_id}")

@reservations.route('/reservations/<int:reservation_id>', methods=['GET'])
@operator_required
def _reservation(reservation_id):

    qry = db.session.query(Booking,User).filter(Booking.id == reservation_id).filter(User.id == Booking.user_id).first()
    
    if qry is None:
        return make_response(render_template('error.html', error='404'),404)
    else:
        if qry.Booking.rest_id != current_user.get_rest_id():
            return make_response(render_template('error.html', error='401'),401)
        
        return render_template("reservation.html", reservation=qry)


@reservations.route('/reservations/<int:reservation_id>/delete', methods=['GET', 'DELETE', 'POST'])
@login_required
def _reservation_delete(reservation_id):

    qry = db.session.query(Booking).filter_by(id = reservation_id).first()
    
    if qry is None:
        return make_response(render_template('error.html', error='404'),404)
    else:
        if qry.rest_id != current_user.get_rest_id() and qry.user_id != current_user.id:
            return make_response(render_template('error.html', error='401'),401)
        else:
            db.session.query(Booking).filter_by(id = reservation_id).delete()
            db.session.commit()
            flash("Reservation deleted","success")
            return redirect('/')

@reservations.route('/reservations/<int:reservation_id>/edit', methods=['GET', 'POST'])
@login_required
def _reservation_edit(reservation_id):

    qry = db.session.query(Booking).filter_by(id = reservation_id).first()
    
    if qry is None:
        return make_response(render_template('error.html', error='404'),404)
    else:
        if qry.user_id != current_user.id:
            return make_response(render_template('error.html', error='401'),401)
        else:
            if current_user.is_positive:
                flash("You cannot book as long as you are positive","error")
                return make_response(render_template('error.html', error="401"), 401)

            now = datetime.datetime.now()

            if qry.booking_datetime <= now:
                flash("The reservation has expired","error")
                return make_response(render_template('error.html', error='404'), 404)

            restaurant_id = qry.rest_id

            form = BookingForm()
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

                    if try_to_update(qry, int(number_of_people), booking_datetime):
                        flash("The changes were confirmed","success")
                        return redirect(f"/restaurants/{restaurant_id}")
                    else: 
                        flash("The reservation could not be made","error")
                        return make_response(render_template('form.html', form=form, title = "Edit your booking"),400)
            elif request.method == "GET":
                obj = {}
                obj["number_of_people"] = qry.people_number
                obj["booking_date"] = qry.booking_datetime.strftime('%d/%m/%Y')
                obj["booking_hr"] = int(qry.booking_datetime.strftime('%H'))
                obj["booking_min"] = int((int(qry.booking_datetime.strftime('%M'))/15))*15 #round to a multiple of 15
                
            return render_template('edit-form.html', form=form, edited=obj, title = "Edit your booking")