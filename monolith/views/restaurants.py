from flask import Blueprint, redirect, render_template, request, make_response, flash
from flask_googlemaps import Map
from monolith.gateway import get_getaway
from monolith.auth import current_user,operator_required
from flask_login import current_user,  login_required
from monolith.forms import  RestaurantEditForm, TableAddForm, SearchRestaurantForm, RatingAddForm
from datetime import datetime, timedelta
from dateutil import parser
from dotmap import DotMap

restaurants = Blueprint('restaurants', __name__)


@restaurants.route('/restaurants')
def _restaurants(message=''):
    """ get the list of restaurants

        Error status code:
            500 -- Error try again later
    """
    allrestaurants, status = get_getaway().get_restaurants()

    if allrestaurants is None or status != 200:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template('error.html', error = status),500)

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
                           base_url="/restaurants")


@restaurants.route('/restaurants/search', methods=["GET", "POST"])
def search_res():
    """
    It allows you to filter the search for restaurants based on the desired characteristics

    Error status code:
        400 -- The form is filled out incorrectly
        404 -- No restaurant with those characteristics was found
        500 -- Error try again later
    Success codes:
        200
    """
    form = SearchRestaurantForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            opening_time = request.form["opening_time"]
            if opening_time.lower() == "not specified":
                opening_time = None
            open_day = request.form["open_day"]
            if open_day == "0":
                open_day = None
            name = request.form["name"]
            if name == "":
                name = None
            cuisine_type = request.form["cuisine_type"]
            if cuisine_type == "":
                cuisine_type = None
            menu = request.form["menu"]
            if menu == "":
                manu = None
            
            allrestaurants, status = get_getaway().get_restaurants(name, opening_time, open_day, cuisine_type, menu)
    
            if allrestaurants is None or status != 200:
                if status == None:
                    flash("Sorry, an error occured. Please, try again.","error")
                    return make_response(render_template('error.html', error = status),500)
                flash("Bad form", "error")
                return make_response(render_template("error.html", error = status), status)

            markers_to_add = []
            matches = []
            for restaurant in allrestaurants:
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

            sndmap = Map( # make the maps of restaurants
                identifier="sndmap",
                lat=43.72,
                lng=10.40,
                markers=markers_to_add,
                zoom_control=True,
                style="height:600px;width:1000px;margin:0;",
                zoom=15
            )
            return render_template("restaurants.html", sndmap=sndmap, restaurants=matches,
                                   base_url="/restaurants")
        flash("Bad form", "error")
        return make_response(render_template('form.html', form=form, title="Find a restaurant!"), 400)
    return make_response(render_template('form.html', form=form, title="Find a restaurant!"), 200)


@restaurants.route('/restaurants/<int:restaurant_id>')
def restaurant_sheet(restaurant_id):
    """ Shows the profile page of a restaurant, which includes its name,
    ratings, position on the map, opening hours etc.

    Error status code:
        404 -- No restaurant with id restaurant_id was found
        500 -- Error try again later
    Success codes:
        200
    """

    restaurant, status = get_getaway().get_restaurant(restaurant_id)
    if restaurant is None or status != 200:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template('error.html', error = status),500)

    tables, status = get_getaway().get_restaurants_tables(restaurant_id)
    if tables is None or status != 200:
        if status == None:
            flash("Sorry, an error occured. Please, try again.","error")
            return make_response(render_template('error.html', error = status),500)
        elif status == 404:
            flash("No restaurant with id restaurant_id was found", "error")
            return make_response(render_template("error.html", error = status), status)
        elif status == 204:
            tables = []

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    closed_days = []
    for day in restaurant.closed_days:
        closed_days.append(days[int(day) - 1])
    form = RatingAddForm()
    return render_template("restaurantsheet.html",
                           name=restaurant.name,
                           rating_val=restaurant.rating_val,
                           rating_num=restaurant.rating_num,
                           lat=restaurant.lat,
                           lon=restaurant.lon,
                           phone=restaurant.phone,
                           id=restaurant_id,
                           closed_days=closed_days,
                           first_opening_hour=restaurant.first_opening_hour,
                           first_closing_hour=restaurant.first_closing_hour,
                           second_opening_hour=restaurant.second_opening_hour,
                           second_closing_hour=restaurant.second_closing_hour,
                           cuisine_type=restaurant.cuisine_type,
                           menu=restaurant.menu,
                           tables=tables,
                           form=form)


@restaurants.route('/restaurants/<int:restaurant_id>/rate', methods=["POST"])
@login_required
def _rate(restaurant_id):
    """ Submits a rating to a restaurant, in a range from 1 to 5

    Error status code:
        400 -- The currently logged-in user has already rated this restaurant, or
               the request is malformed
        401 -- The user is not logged-in
        404 -- No restaurant with id restaurant_id was found
        500 -- Error try again later
    Success codes:
        200
    """

    form = RatingAddForm()
    if form.validate_on_submit():
        rating,status = get_getaway().post_restaurant_rate(restaurant_id, current_user.id, form.rating.data)
        if rating is None or status != 202:
            if status == None:
                flash("Sorry, an error occured. Please, try again.","error")
                return make_response(render_template('error.html', error = status),500)
            elif status == 400:
                flash('Bad request or Restaurant already rated by the user', "error")
            elif status == 404:
                flash('No restaurant with id restaurant_id was found', "error")
            elif status == 500:
                flash("Sorry, an error occured. Please, try again. [2]","error")
            return make_response(render_template("error.html", error = status), status)
        
        flash('Rating submitted', "success")
        return restaurant_sheet(restaurant_id)
    flash("Bad form", "error")
    return make_response(restaurant_sheet(restaurant_id), 400)

@restaurants.route('/create_restaurant', methods=['GET', 'POST'])
@operator_required
def _create_restaurant():
    """ Show the page for editing the restaurant with GET, the form can be submitted with POST

    Error status codes:
        400 -- The request is not valid, the form is filled out incorrectly or a generic error has occurred
        404 -- The restaurant does not exists
        409 -- The current user is not an operator or the operator of this restaurant
        500 -- Error try again later

    Success codes:
        200 GET  -- The form is sent to the user
        302 POST -- The modification was accepted
    """

    if current_user.rest_id != None:
        return make_response(render_template('error.html', error="Restaurant already created"), 401)

    if request.method == 'POST':
        form = RestaurantEditForm()
        if form.validate_on_submit():
            json = DotMap()
            form.populate_obj(json)
            json = json.toDict()
            json["closed_days"] = [int(i) for i in json["closed_days"]]
            restaurant,status = get_getaway().post_restaurants(json)
            if restaurant is None or status != 201:
                if status == None or status == 500:
                    flash("Sorry, an error occured. Please, try again.","error")
                    return make_response(render_template('error.html', error = status),500)
                elif status == 400:
                    flash('Bad request', "error")
                return make_response(render_template("error.html", error = status), status)
            user,status = get_getaway().set_user_restaurant(current_user.id, restaurant.id)
            if user is None or status != 200:
                restaurant,status2 = get_getaway().delete_restaurant(restaurant.id)
                flash("Sorry, an error occured. Please, try again.","error")
                return make_response(render_template('error.html', error = status),500)
            return redirect(f"/restaurants/{current_user.rest_id}")
        flash("Bad form", "error")
        return make_response(render_template('edit_restaurant.html', form=form), 400)
    form = RestaurantEditForm()
    return render_template('edit_restaurant.html', form=form)


@restaurants.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@operator_required
def _edit_restaurant(restaurant_id):
    """ Show the page for editing the restaurant with GET, the form can be submitted with POST

    Error status codes:
        400 -- The request is not valid, the form is filled out incorrectly or a generic error has occurred
        404 -- The restaurant does not exists
        409 -- The current user is not an operator or the operator of this restaurant
        500 -- Error try again later

    Success codes:
        200 GET  -- The form is sent to the user
        302 POST -- The modification was accepted
    """
    restaurant, status = get_getaway().get_restaurant(restaurant_id)
    if restaurant is None or status != 200:
        flash("Sorry, an error occured. Please, try again.","error")
        return make_response(render_template('error.html', error = status),500)

    if current_user.rest_id != restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    if request.method == 'POST':
        form = RestaurantEditForm()
        if form.validate_on_submit():
            json = DotMap()
            form.populate_obj(json)
            json = json.toDict()
            json["closed_days"] = [int(i) for i in json["closed_days"]]
            restaurant,status = get_getaway().edit_restaurant(restaurant_id, json)
            if restaurant is None or status != 200:
                if status == None:
                    flash("Sorry, an error occured. Please, try again.","error")
                    return make_response(render_template('error.html', error = status),500)
                elif status == 400:
                    flash('Bad request or Restaurant already rated by the user', "error")
                elif status == 404:
                    flash('No restaurant with id restaurant_id was found', "error")
                elif status == 409:
                    flash('The restaurant has pending reservations tha conflict with the new openings, those must be deleted first', "error")
                elif status == 500:
                    flash("Sorry, an error occured. Please, try again. [2]","error")
                return make_response(render_template("error.html", error = status), status)
            return redirect(f"/restaurants/{current_user.rest_id}")
        flash("Bad form", "error")
        return make_response(render_template('edit_restaurant.html', form=form), 400)
    form = RestaurantEditForm(obj=restaurant)
    return render_template('edit_restaurant.html', form=form)

@restaurants.route('/restaurants/<int:restaurant_id>/overview')
@operator_required
def restaurant_reservations_overview_today(restaurant_id):
    """ Alias for today's reservations overview """

    today = datetime.today()
    return restaurant_reservations_overview(restaurant_id,today.year,today.month,today.day)

@restaurants.route('/restaurants/<int:restaurant_id>/overview/<int:year>/<int:month>/<int:day>')
@operator_required
def restaurant_reservations_overview(restaurant_id, year, month, day):
    """ Renders an overview of a day's reservations
    
    If GET parameters from_h, from_m, to_h, to_m are provided, also renders the
    list of reservations in the particular time range.

    Error status codes:
        400 -- The requested time range is invalid
        401 -- The request has been sent by an unauthenticated user, or the user
                is not the owner of the restaurant
        404 -- The restaurant or the requested day do not exist
    """

    try:
        date_start = datetime(year, month, day)
        prev_day = date_start - timedelta(days=1)
        date_end = date_start + timedelta(days=1)
    except:
        return make_response(render_template('error.html', error='404'), 404)

    if current_user.rest_id != restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    restaurant, status = get_getaway().get_restaurant(restaurant_id)

    if restaurant is None or status != 200:
        return make_response(render_template('error.html', error=status), status)

    reservations, status = get_getaway().get_bookings(
        None,                   # User
        restaurant_id,          # Restaurant
        None,                   # Table
        date_start.isoformat(), # Begin
        date_end.isoformat(),   # End
        None,                   # Entrance begin
        None,                   # Entrance end
        False)                  # With user

    if reservations is None or status != 200:
        return make_response(render_template('error.html', error=status), status)

    lunch_reservations = []
    dinner_reservations = []

    if restaurant.first_opening_hour is not None:
        slot_begin = datetime(year, month, day, restaurant.first_opening_hour)
        slot_end = datetime(year, month, day, restaurant.first_closing_hour)

        for reserv in reservations:
            booking_datetime = parser.parse(reserv.booking_datetime, ignoretz = True)
            if booking_datetime >= slot_begin and booking_datetime < slot_end:
                lunch_reservations.append(reserv)

    if restaurant.second_opening_hour is not None:
        slot_begin = datetime(year, month, day, restaurant.second_opening_hour)
        slot_end = datetime(year, month, day, restaurant.second_closing_hour)

        for reserv in reservations:
            booking_datetime = parser.parse(reserv.booking_datetime, ignoretz = True)
            if booking_datetime >= slot_begin and booking_datetime < slot_end:
                dinner_reservations.append(reserv)

    slot_begin = None
    slot_end = None
    slot_reservations = None
    people_total = None

    if request.args.get('from_h') is not None and \
        request.args.get('from_m') is not None and \
        request.args.get('to_h') is not None and \
        request.args.get('to_m') is not None:
        try:
            from_h = int(request.args.get('from_h'))
            from_m = int(request.args.get('from_m'))
            to_h = int(request.args.get('to_h'))
            to_m = int(request.args.get('to_m'))

            slot_begin = datetime(year, month, day, from_h, from_m)
            slot_end = datetime(year, month, day, to_h, to_m)
        except:
            return make_response(render_template('error.html', error='Invalid slot range'), 400)

        if slot_end < slot_begin:
            return make_response(render_template('error.html', error='Slot start must be before slot end'), 400)

        slot_reservations, status = get_getaway().get_bookings(
            None,                   # User
            restaurant_id,          # Restaurant
            None,                   # Table
            slot_begin.isoformat(), # Begin
            slot_end.isoformat(),   # End
            None,                   # Entrance begin
            None,                   # Entrance end
            False)                  # With user
        
        if slot_reservations is None or status != 200:
            return make_response(render_template('error.html', error=status), status)

        people_total = 0
        for reserv in slot_reservations:
            people_total = people_total + reserv.number_of_people

    return render_template('overview.html',
        restaurant = restaurant,
        lunch=lunch_reservations,
        dinner=dinner_reservations,
        current = date_start,
        prev = prev_day,
        next = date_end,
        today = datetime.today(),
        slot_begin = slot_begin,
        slot_end = slot_end,
        slot_reservations = slot_reservations,
        slot_people = people_total)

@restaurants.route('/tables/add', methods=['GET', 'POST'])
@operator_required
def _add_tables():
    """ Adds a new table to the current user's restaurant

    Error status codes:
        400 -- The requested table capacity is invalid, or the request is malformed
        401 -- The request has been sent by an unauthenticated user, or the user
                is not the owner of a restaurant
        500 -- Error, try again later

    Success codes:
        200 -- The form is sent to the user
        302 -- The addition is accepted
    """

    form = TableAddForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            table, status = get_getaway().post_restaurants_tables(current_user.rest_id, int(request.form['capacity']))
            if table is None or status != 201:
                if status == None or status == 404:
                    flash("Sorry, an error occured. Please, try again.","error")
                    return make_response(render_template('error.html', error = status),500)
                flash("Bad form", "error")
                return make_response(render_template("error.html", error = status), status)
            return redirect(f"/restaurants/{current_user.rest_id}")
        flash("Bad form", "error")
        return make_response(render_template('form.html', form=form), 400)
    return make_response(render_template('form.html', form=form), 200)


@restaurants.route('/tables/<int:table_id>/edit', methods=['GET', 'POST'])
@operator_required
def _edit_tables(table_id):
    """ Edits the info of a table

    Error status codes:
        400 -- The requested table capacity is invalid, or the request is malformed
        401 -- The request has been sent by an unauthenticated user, or
               the user is not the owner of the table's restaurant
        404 -- A table with id table_id has not been found
        409 -- The table has pending reservations tha conflict with the new capacity, those must be deleted first
        500 -- Error, try again later

    Success codes:
        200 GET  -- The form is sent to the user
        302 POST -- The edit is accepted
    """
    
    table, status = get_getaway().get_restaurants_table(current_user.rest_id, table_id)
    if table is None or status != 200:
        if status == None:
            flash("Sorry, an error occured. Please, try again.","error")
            return make_response(render_template('error.html', error = status),500)
        flash("A table with such id has not been found","error")
        return make_response(render_template("error.html", error = status), status)

    if current_user.rest_id != table.restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)

    if request.method == 'POST':
        form = TableAddForm()
        if form.validate_on_submit():
            table, status = get_getaway().edit_restaurants_table(current_user.rest_id, table_id, capacity = int(request.form['capacity']))
            if table is None or status != 200:
                if status == None or status == 500 or status == 404:
                    flash("Sorry, an error occured. Please, try again.","error")
                    return make_response(render_template('error.html', error = status),500)
                elif status == 400:
                    flash("Bad form", "error")
                elif status == 409:
                    flash("The table has pending reservations tha conflict with the new capacity, those must be deleted first","error")
                return make_response(render_template("error.html", error = status), status)
            return redirect(f"/restaurants/{current_user.rest_id}")
        flash("Bad form", "error")
        return make_response(render_template('form.html', form=form), 400)
    form = TableAddForm(obj=table)
    return make_response(render_template('form.html', form=form), 200)


@restaurants.route('/tables/<int:table_id>/delete')
@operator_required
def delete_table(table_id):
    """ Deletes a table

    Error status codes:
        401 -- The request has been sent by an unauthenticated user, or
               the user is not the owner of the table's restaurant
        404 -- A table with id table_id has not been found
        409 -- The table has pending reservations, those must be deleted first
        500 -- Error, try again later

    Success codes:
        302 -- The deletion is accepted
    """

    table, status = get_getaway().get_restaurants_table(current_user.rest_id, table_id)
    if table is None or status != 200:
        if status == None:
            flash("Sorry, an error occured. Please, try again.","error")
            return make_response(render_template('error.html', error = status),500)
        flash("A table with such id has not been found","error")
        return make_response(render_template("error.html", error = status), status)

    if current_user.rest_id != table.restaurant_id:
        return make_response(render_template('error.html', error="Area reserved for the restaurant operator"), 401)


    table, status = get_getaway().delete_restaurants_table(current_user.rest_id, table_id)
    if status != 204:
        if status == None or status == 404 or status == 500:
            flash("Sorry, an error occured. Please, try again.","error")
            return make_response(render_template('error.html', error = status),500)
        elif status == 409:
            flash("The table has pending reservations, those must be deleted first","error")
        return make_response(render_template("error.html", error = status), status)
    return redirect(f'/restaurants/{current_user.rest_id}')
