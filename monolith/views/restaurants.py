from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.database import db, Restaurant, Like, Booking
from monolith.auth import admin_required, current_user, is_admin
from flask_login import (current_user, login_user, logout_user,
                         login_required)
from monolith.forms import UserForm, BookingForm
import datetime

restaurants = Blueprint('restaurants', __name__)

@restaurants.route('/restaurants')
def _restaurants(message=''):
    allrestaurants = db.session.query(Restaurant)
    return render_template("restaurants.html", message=message, restaurants=allrestaurants, base_url="http://127.0.0.1:5000/restaurants")

@restaurants.route('/restaurants/<restaurant_id>')
def restaurant_sheet(restaurant_id):
    record = db.session.query(Restaurant).filter_by(id = int(restaurant_id)).all()[0]
    return render_template("restaurantsheet.html", name=record.name, likes=record.likes, lat=record.lat, lon=record.lon, phone=record.phone, id=restaurant_id)
    
@restaurants.route('/restaurants/like/<restaurant_id>')
@login_required
def _like(restaurant_id):
    q = Like.query.filter_by(liker_id=current_user.id, restaurant_id=restaurant_id)
    if q.first() != None:
        new_like = Like()
        new_like.liker_id = current_user.id
        new_like.restaurant_id = restaurant_id
        db.session.add(new_like)
        db.session.commit()
        message = ''
    else:
        message = 'You\'ve already liked this place!'
    return _restaurants(message)

def try_to_book(restaurant_id, number_of_person, booking_date, booking_hr, booking_min):
    record = db.session.query(Restaurant).filter_by(id = int(restaurant_id)).all()[0]
    if record.is_open(booking_date, booking_hr, booking_min):
        q = Booking.query.filter_by(rest_id=restaurant_id, booking_date=booking_date)
        print(q)
        if q.first() != None:
            new_booking = Booking()
            new_booking.user_id = current_user.id
            new_booking.rest_id = restaurant_id
            new_booking.person_number = number_of_person
            new_booking.booking_date = booking_date
            new_booking.booking_hr = booking_hr
            new_booking.booking_min = booking_min
            db.session.add(new_booking)
            db.session.commit()
            return True
    return False

@restaurants.route('/restaurants/book/<restaurant_id>', methods=['GET', 'POST'])
@login_required
def _book(restaurant_id):
    if False and is_admin or current_user.is_operator:
        flash("Please log as customer to book a table","error")
        return redirect("/restaurants/"+restaurant_id)
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

            if try_to_book(restaurant_id, int(number_of_person), booking_date, int(booking_hr), int(booking_min)):
                flash("The booking was confirmed","success")
                return redirect("/restaurants/"+restaurant_id)
            else:
                flash("The reservation could not be made","error")
                return render_template('book_a_table.html', form=form)

    return render_template('book_a_table.html', form=form)