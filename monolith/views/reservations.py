from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.database import db, Restaurant, Like, Booking, User, Table
from monolith.auth import admin_required, current_user, is_admin, operator_required
from flask_login import current_user, login_user, logout_user, login_required
from monolith.forms import UserForm, BookingForm, BookingList
import datetime


def book_a_table(restaurant, number_of_person, booking_datetime, table):
    new_booking = Booking()
    new_booking.user_id = current_user.id
    new_booking.rest_id = restaurant.id
    new_booking.person_number = number_of_person
    new_booking.booking_datetime = booking_datetime
    new_booking.table_id = table
    db.session.add(new_booking)
    db.session.commit()


def get_table(restaurant, number_of_person, booking_datetime):
    delta = restaurant.occupation_time
    starting_period = booking_datetime - datetime.timedelta(hours=delta)
    ending_period = booking_datetime + datetime.timedelta(hours=delta)
    occupied = db.session.query(Table.id).select_from(Booking,Table)\
                        .filter(Booking.table_id == Table.id)\
                        .filter(Booking.rest_id == restaurant.id)\
                        .filter(starting_period < Booking.booking_datetime)\
                        .filter(Booking.booking_datetime < ending_period )\
                        .all() #GB < or <= ? Better <

    total = db.session.query(Table.id,Table.capacity).select_from(Table,Restaurant)\
                        .filter(Restaurant.id == Table.rest_id)\
                        .all()

    free_tables = [t for t in total if ( ( (t[0],) not in occupied) and (t[1] >= number_of_person) )]
    free_tables.sort(key=lambda x:x[1])

    if free_tables == []:
        return None
    return free_tables[0][0]


def try_to_book(restaurant_id, number_of_person, booking_datetime):
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).all()[0]
    if record.is_open(booking_datetime):
        table = get_table(record, number_of_person, booking_datetime)
        if table is not None:
            book_a_table(record, number_of_person, booking_datetime, table)
            return True
    return False

@restaurants.route('/restaurants/<int:restaurant_id>/book', methods=['GET', 'POST'])
@login_required
def _book(restaurant_id):

    if current_user.is_admin or current_user.is_operator:
        flash("Please log as customer to book a table","error")
        return redirect(f"/restaurants/{restaurant_id}")

    if current_user.is_positive:
        flash("You cannot book as long as you are positive","error")
        return redirect(f"/restaurants/{restaurant_id}")

    form = BookingForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            number_of_person = request.form["number_of_person"]
            booking_date = request.form["booking_date"]
            booking_hr = request.form["booking_hr"]
            booking_min = request.form["booking_min"]

            now = datetime.datetime.now()
            day, month, year = (int(x) for x in booking_date.split('/'))   
            booking_datetime = now.replace(year=year,month=month,day=day,hour=int(booking_hr),minute=int(booking_min),second=0,microsecond=0)
            
            if booking_datetime < now:
                flash("You cannot book before now","error")
                return render_template('book_a_table.html', form=form)

            if try_to_book(restaurant_id, int(number_of_person), booking_datetime):
                flash("The booking was confirmed","success")
                return redirect(f"/restaurants/{restaurant_id}")
            else:
                flash("The reservation could not be made","error")
                return render_template('book_a_table.html', form=form)

    return render_template('book_a_table.html', form=form)


@restaurants.route('/restaurants/<int:restaurant_id>/reservations', methods=['GET', 'POST'])
@operator_required
def _booking_list(restaurant_id):

    if current_user.rest_id != restaurant_id:
        flash("Area reserved for the restaurant operator","error")
        return redirect(f"/restaurants/{restaurant_id}", code=401)

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
                return render_template('booking_list.html', form=form)

            qry = db.session.query(Booking,User)\
                            .filter_by(rest_id = current_user.get_rest_id())\
                            .filter(User.id == Booking.user_id)\
                            .filter(from_datetime <= Booking.booking_datetime)\
                            .filter(Booking.booking_datetime <= to_datetime )\
                            .all()

            return render_template("reservations.html", reservations=qry)

    return render_template('booking_list.html', form=form)



@restaurants.route('/reservations/<int:reservation_id>', methods=['GET'])
@operator_required
def _reservation(reservation_id):

    qry = db.session.query(Booking,User).filter(Booking.id == reservation_id).filter(User.id == Booking.user_id).all()
    
    if qry == []:
        return make_response(render_template('error.html', error='404'),404)
    else:
        qry = qry[0]
        if qry.Booking.rest_id != current_user.get_rest_id():
            return make_response(render_template('error.html', error='401'),401)
        else:
            return render_template("reservation.html", reservation=qry)

@restaurants.route('/reservations/<int:reservation_id>/delete', methods=['GET', 'POST'])
@operator_required
def _reservation(reservation_id):

    qry = db.session.query(Booking,User).filter(Booking.id == reservation_id).filter(User.id == Booking.user_id).all()
    
    if qry == []:
        return make_response(render_template('error.html', error='404'),404)
    else:
        qry = qry[0]
        if qry.Booking.rest_id != current_user.get_rest_id():
            return make_response(render_template('error.html', error='401'),401)
        else:
            db.session.query(Booking).filter_by(id = reservation_id).delete()
            db.session.commit()
            flash("Reservation deleted","success")
            return redirect('/')