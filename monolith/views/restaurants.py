from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.database import db, Restaurant, Like, Booking, User, Table
from monolith.auth import admin_required, current_user, is_admin, operator_required
from flask_login import current_user, login_user, logout_user, login_required
from monolith.forms import UserForm, BookingForm, BookingList
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
    
@restaurants.route('/restaurants/<int:restaurant_id>/like')
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

@restaurants.route('/tables/<int:table_id>/delete')
@operator_required
def delete_table(table_id):
    table = db.session.query(Table).filter(Table.id == table_id).first()

    if table == None:
        return make_response(render_template('error.html', error='404'), 404)

    if table.bookings != []:
        return make_response(render_template('error.html', error="Table is already booked"), 412)

    if table.rest_id == current_user.rest_id:
        db.session.delete(table)
        db.session.commit()
        return redirect(f'/restaurants/{current_user.rest_id}')
    else:
        return make_response(render_template('error.html', error='401'),401)