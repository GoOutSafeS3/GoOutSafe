from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.database import db, Restaurant, Like, Booking, User, Table
from monolith.auth import admin_required, current_user, is_admin, operator_required
from flask_login import current_user, login_user, logout_user, login_required
from monolith.forms import UserForm, BookingForm, BookingList, RestaurantEditForm, TableAddForm
from monolith.utilities.restaurant import is_busy_table
restaurants = Blueprint('restaurants', __name__)

@restaurants.route('/restaurants')
def _restaurants(message=''):
    allrestaurants = db.session.query(Restaurant)
    return render_template("restaurants.html", message=message, restaurants=allrestaurants, base_url="http://127.0.0.1:5000/restaurants")

@restaurants.route('/restaurants/<int:restaurant_id>')
def restaurant_sheet(restaurant_id):
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).first()
    if record is None:
        return make_response(render_template('error.html', error='404'),404)

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
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).first()
    if record is None:
        return make_response(render_template('error.html', error='404'),404)

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

@restaurants.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@operator_required
def _edit_restaurant(restaurant_id):
    
    record = db.session.query(Restaurant).filter_by(id = restaurant_id).first()

    if record is None:
        return make_response(render_template('error.html', error='404'), 404)

    if current_user.rest_id != restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    if request.method == 'POST':
        form = RestaurantEditForm()
        if form.validate_on_submit():
            form.populate_obj(record)
            record.closed_days = ''.join(request.form.getlist('closed_days'))
            db.session.add(record)
            db.session.commit()
            return redirect(f"/restaurants/{current_user.rest_id}")
        flash("Bad form","error")
        return make_response(render_template('edit_restaurant.html', form=form), 400)
    form = RestaurantEditForm(obj=record)
    return render_template('edit_restaurant.html', form=form)

@restaurants.route('/tables/add', methods=['GET', 'POST'])
@operator_required
def _add_tables():
    form = TableAddForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            table = Table()
            table.rest_id = current_user.rest_id
            table.capacity = int(request.form['capacity'])
            if table.capacity > 0:
                db.session.add(table)
                db.session.commit()
                return redirect(f"/restaurants/{current_user.rest_id}")
            flash("Capacity must be strictly positive","error")
            return make_response(render_template('form.html', form=form), 400)
        flash("Bad form","error")
        return make_response(render_template('form.html', form=form), 400)
    return make_response(render_template('form.html', form=form), 200)

@restaurants.route('/tables/<int:table_id>/edit', methods=['GET', 'POST'])
@operator_required
def _edit_tables(table_id):
    table = db.session.query(Table).filter(Table.id == table_id).first()

    if table is None:
        return make_response(render_template('error.html', error='404'), 404)

    if current_user.rest_id != table.rest_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    if request.method == 'POST':
        form = TableAddForm()
        if form.validate_on_submit():
            capacity = int(request.form['capacity'])
            if capacity > 0:
                table.capacity = capacity
                db.session.add(table)
                db.session.commit()
                return redirect(f"/restaurants/{current_user.rest_id}")
            flash("Capacity must be strictly positive","error")
            return make_response(render_template('form.html', form=form), 400)
        flash("Bad form","error")
        return make_response(render_template('form.html', form=form), 400)
    form = TableAddForm(obj=table)
    return make_response(render_template('form.html', form=form), 200)

@restaurants.route('/tables/<int:table_id>/delete')
@operator_required
def delete_table(table_id):
    table = db.session.query(Table).filter(Table.id == table_id).first()

    if table is None:
        return make_response(render_template('error.html', error='404'), 404)

    if table.bookings != []:
        if is_busy_table(table_id):
            return make_response(render_template('error.html', error="Table is already booked"), 412)

    if table.rest_id == current_user.rest_id:
        db.session.delete(table)
        db.session.commit()
        return redirect(f'/restaurants/{current_user.rest_id}')
    else:
        return make_response(render_template('error.html', error='401'),401)