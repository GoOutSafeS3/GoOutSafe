from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.database import db, Restaurant, Like, Booking, User, Table
from monolith.auth import admin_required, current_user, is_admin, operator_required
from flask_login import current_user, login_user, logout_user, login_required
from monolith.forms import UserForm, BookingForm, BookingList, RestaurantEditForm
import datetime

restaurants = Blueprint('restaurants', __name__)

@restaurants.route('/restaurants')
def _restaurants(message=''):
    allrestaurants = db.session.query(Restaurant)
    return render_template("restaurants.html", message=message, restaurants=allrestaurants, base_url="http://127.0.0.1:5000/restaurants")

@restaurants.route('/restaurants/<int:restaurant_id>')
def restaurant_sheet(restaurant_id):
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).all()[0]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    closed_days = []
    for day in record.closed_days:
        closed_days.append(days[int(day) - 1])

    return render_template("restaurantsheet.html",
        name=record.name,
        likes=record.likes,
        lat=record.lat,
        lon=record.lon,
        phone=record.phone,
        id=restaurant_id,
        closed_days=closed_days,
        lunch_opening=record.opening_hour_lunch,
        lunch_closing=record.closing_hour_lunch,
        dinner_opening=record.opening_hour_dinner,
        dinner_closing=record.closing_hour_dinner,
        cuisine_type=record.cuisine_type,
        menu=record.menu,
        tables=record.tables)
    
@restaurants.route('/restaurants/like/<int:restaurant_id>')
@login_required
def _like(restaurant_id):
    q = Like.query.filter_by(liker_id=current_user.id, restaurant_id=restaurant_id)
    if q.first() == None:
        new_like = Like()
        new_like.liker_id = current_user.id
        new_like.restaurant_id = restaurant_id
        db.session.add(new_like)
        db.session.commit()
        message = ''
    else:
        message = 'You\'ve already liked this place!'
    return _restaurants(message)

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
                        .filter(starting_period <= Booking.booking_datetime)\
                        .filter(Booking.booking_datetime <= ending_period )\
                        .all()

    total = db.session.query(Table.id,Table.capacity).select_from(Table,Restaurant)\
                        .filter(Restaurant.id == Table.rest_id)\
                        .all()

    free_tables = [t for t in total if ( ( (t[0],) not in occupied) and (t[1] >= number_of_person) )]
    free_tables.sort(key=lambda x:x[1])

    print(occupied)
    print(total)
    print(free_tables)

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

@restaurants.route('/restaurants/book/<int:restaurant_id>', methods=['GET', 'POST'])
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

@restaurants.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@operator_required
def _edit_restaurant(restaurant_id):
    
    if current_user.rest_id != restaurant_id:
        flash("Area reserved for the restaurant operator","error")
        return redirect(f"/restaurants/{restaurant_id}", code=401)

    record = db.session.query(Restaurant).filter_by(id = restaurant_id).all()[0]

    form = RestaurantEditForm(obj=record)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(record)
            record.closed_days = ''.join(request.form['closed_days'])
            db.session.add(record)
            db.session.commit()
            flash("Updated","success")
            return render_template("edit_restaurant.html", form=form)
    flash(record.name,"success")
    return render_template('edit_restaurant.html', form=form)


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



@restaurants.route('/reservations/<int:reservation_id>', methods=['GET', 'DELETE', 'POST'])
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
            if request.method == "DELETE" or request.method == "POST":
                db.session.query(Booking).filter_by(id = reservation_id).delete()
                db.session.commit()
                flash("Reservation deleted","success")
                return redirect('/')
            
            elif request.method == "GET":
                return render_template("reservation.html", reservation=qry)

@restaurants.route('/tables/delete/<int:table_id>')
@operator_required
def delete_table(table_id):
    table = db.session.query(Table).filter(Table.id == table_id).first()

    if table == None:
        return make_response(render_template('error.html', error='404'), 404)

    if table.bookings != []:
        return make_response(render_template('error.html', error="Table is already booked"), 412)

    if table.rest_id == current_user.rest_id:
        db.session.delete(table)
        return redirect(f'/restaurants/{current_user.rest_id}')
    else:
        return make_response(render_template('error.html', error='401'),401)