from flask import Blueprint, redirect, render_template, request, make_response, flash
from flask_googlemaps import Map
from monolith.utilities.restaurant import validate_hours
from monolith.database import db, Restaurant, Like, Booking, User, Table
from monolith.auth import admin_required, current_user, is_admin, operator_required
from flask_login import current_user, login_user, logout_user, login_required
from monolith.forms import UserForm, BookingForm, BookingList, RestaurantEditForm, TableAddForm, SearchRestaurantForm
from monolith.utilities.restaurant import is_busy_table
from datetime import datetime, timedelta

restaurants = Blueprint('restaurants', __name__)


@restaurants.route('/restaurants')
def _restaurants(message=''):
    allrestaurants = db.session.query(Restaurant)
    markers_to_add = []
    for restaurant in allrestaurants:
        rest = {
            'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
            'lat': restaurant.lat,
            'lng': restaurant.lon,
            'infobox': restaurant.name
        }
        markers_to_add.append(rest)
    sndmap = Map(
        identifier="sndmap",
        lat=43.72,
        lng=10.40,
        markers=markers_to_add,
        zoom_control=True,
        style="height:600px;width:1000px;margin:0;",
        zoom=15
    )
    return render_template("restaurants.html", message=message, sndmap=sndmap, restaurants=allrestaurants,
                           base_url="http://127.0.0.1:5000/restaurants")


@restaurants.route('/restaurants/search', methods=["GET", "POST"])
def search_res():
    form = SearchRestaurantForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            allrestaurants = db.session.query(Restaurant).all()

            markers_to_add = []
            matches = []
            for restaurant in allrestaurants:

                if request.form["name"].lower() in restaurant.name.lower() \
                        and request.form["cuisine_type"].lower() in restaurant.cuisine_type.lower() \
                        and request.form["menu"].lower() in restaurant.menu.lower() \
                        and request.form["open_day"].lower() not in restaurant.closed_days.lower() \
                        and ( \
                                (request.form["opening_time"].lower() == "not specified") \
                                or (
                                        restaurant.opening_hour_lunch is not None and restaurant.closing_hour_lunch is not None and restaurant.opening_hour_lunch <= int(
                                    request.form["opening_time"]) <= restaurant.closing_hour_lunch) \
                                or (
                                        restaurant.opening_hour_dinner is not None and restaurant.closing_hour_dinner is not None and restaurant.opening_hour_dinner <= int(
                                    request.form["opening_time"]) <= restaurant.closing_hour_dinner) \
                        ):
                    rest = {
                        'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                        'lat': restaurant.lat,
                        'lng': restaurant.lon,
                        'infobox': restaurant.name
                    }
                    markers_to_add.append(rest)
                    matches.append(restaurant)

            if matches == []:
                flash("No restaurant found", "error")
                return make_response(render_template('form.html', form=form, title="Find a restaurant!"), 404)

            sndmap = Map(
                identifier="sndmap",
                lat=43.72,
                lng=10.40,
                markers=markers_to_add,
                zoom_control=True,
                style="height:600px;width:1000px;margin:0;",
                zoom=15
            )
            return render_template("restaurants.html", sndmap=sndmap, restaurants=matches,
                                   base_url="http://127.0.0.1:5000/restaurants")
        flash("Bad form", "error")
        return make_response(render_template('form.html', form=form, title="Find a restaurant!"), 400)
    return make_response(render_template('form.html', form=form, title="Find a restaurant!"), 200)


@restaurants.route('/restaurants/<int:restaurant_id>')
def restaurant_sheet(restaurant_id):
    record = db.session.query(Restaurant).filter_by(id=restaurant_id).first()
    if record is None:
        return make_response(render_template('error.html', error='404'), 404)

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
    record = db.session.query(Restaurant).filter_by(id=restaurant_id).first()
    if record is None:
        return make_response(render_template('error.html', error='404'), 404)

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
    record = db.session.query(Restaurant).filter_by(id=restaurant_id).first()

    if record is None:
        return make_response(render_template('error.html', error='404'), 404)

    if current_user.rest_id != restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    if request.method == 'POST':
        form = RestaurantEditForm()
        if form.validate_on_submit():
            opening_lunch = form.opening_hour_lunch.data
            opening_dinner = form.opening_hour_dinner.data
            closing_lunch = form.closing_hour_lunch.data
            closing_dinner = form.closing_hour_dinner.data
            
            if opening_dinner is not None and opening_lunch is not None and \
               closing_lunch is not None and closing_dinner is not None:
                if not validate_hours(opening_lunch, closing_lunch, opening_dinner, closing_dinner):
                    flash('Closing time cannot be before opening time (general)','error')
                    return make_response(render_template('edit_restaurant.html', form=form),400)
            else:
                if opening_lunch is None or closing_lunch is None:
                    if opening_lunch is not None or closing_lunch is not None:
                        flash('You must specify both lunch hours or none', 'error')
                        return make_response(render_template('edit_restaurant.html', form=form), 400)
                    if opening_dinner > closing_dinner:
                        flash('Closing time cannot be before opening time (dinner)', 'error')
                        return make_response(render_template('edit_restaurant.html', form=form), 400)
                elif opening_dinner is None or closing_dinner is None:
                    if opening_dinner is not None or closing_dinner is not None:
                        flash('You must specify both dinner hours or none', 'error')
                        return make_response(render_template('edit_restaurant.html', form=form), 400)
                    if opening_lunch > closing_lunch:
                        flash('Closing time cannot be before opening time (lunch)', 'error')
                        return make_response(render_template('edit_restaurant.html', form=form), 400)
            form.populate_obj(record)
            record.closed_days = ''.join(request.form.getlist('closed_days'))
            db.session.add(record)
            db.session.commit()
            return redirect(f"/restaurants/{current_user.rest_id}")
        flash("Bad form", "error")
        return make_response(render_template('edit_restaurant.html', form=form), 400)
    form = RestaurantEditForm(obj=record)
    return render_template('edit_restaurant.html', form=form)

@restaurants.route('/restaurants/<int:restaurant_id>/overview')
@operator_required
def restaurant_reservations_overview_today(restaurant_id):
    today = datetime.today()
    return restaurant_reservations_overview(restaurant_id,today.year,today.month,today.day)

@restaurants.route('/restaurants/<int:restaurant_id>/overview/<int:year>/<int:month>/<int:day>')
@operator_required
def restaurant_reservations_overview(restaurant_id, year, month, day):
    try:
        date_start = datetime(year, month, day)
        prev_day = date_start - timedelta(days=1)
        date_end = date_start + timedelta(days=1)
    except:
        return make_response(render_template('error.html', error='404'), 404)

    if current_user.rest_id != restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    restaurant = db.session.query(Restaurant).\
        filter(Restaurant.id == restaurant_id).\
        first()

    if restaurant is None:
        return make_response(render_template('error.html', error='404'), 404)

    reservations = db.session.query(Booking).\
        filter(Booking.rest_id == restaurant_id).\
        filter(Booking.booking_datetime >= date_start).\
        filter(Booking.booking_datetime < date_end).\
        all()

    lunch_reservations = []
    dinner_reservations = []

    if restaurant.opening_hour_lunch is not None:
        slot_begin = datetime(year, month, day, restaurant.opening_hour_lunch)
        slot_end = datetime(year, month, day, restaurant.closing_hour_lunch)

        for reserv in reservations:
            if reserv.booking_datetime >= slot_begin and reserv.booking_datetime < slot_end:
                lunch_reservations.append(reserv)

    if restaurant.opening_hour_dinner is not None:
        slot_begin = datetime(year, month, day, restaurant.opening_hour_dinner)
        slot_end = datetime(year, month, day, restaurant.closing_hour_dinner)

        for reserv in reservations:
            if reserv.booking_datetime >= slot_begin and reserv.booking_datetime < slot_end:
                dinner_reservations.append(reserv)


    return render_template('overview.html',
        restaurant = db.session.query(Restaurant).filter(Restaurant.id == restaurant_id).first(),
        lunch=lunch_reservations,
        dinner=dinner_reservations,
        current = date_start,
        prev = prev_day,
        next = date_end,
        today = datetime.today())

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
            flash("Capacity must be strictly positive", "error")
            return make_response(render_template('form.html', form=form), 400)
        flash("Bad form", "error")
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
            flash("Capacity must be strictly positive", "error")
            return make_response(render_template('form.html', form=form), 400)
        flash("Bad form", "error")
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
        return make_response(render_template('error.html', error='401'), 401)
