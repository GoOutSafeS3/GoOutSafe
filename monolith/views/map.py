from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.gateway import gateway
from flask_login import current_user, login_required
from flask_googlemaps import GoogleMaps, Map

map = Blueprint('map', __name__)


@map.route('/restaurants_map', methods=['GET'])
@login_required
def map_page():
    """ returns a map of all restaurants in GoOutSafe

        You must logged as customer

        Error status codes:
            401 -- If a user other than customer tries to view it
    """
    if current_user.is_admin or current_user.is_health_authority or current_user.rest_id is not None:
        return make_response(render_template('error.html', error='401'), 401)


    restaurants, status = gateway.get_restaurants()
    markers_to_add = []
    for restaurant in restaurants:
        rest = {
            'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
            'lat': restaurant['lat'],
            'lng': restaurant['lon'],
            'infobox': restaurant['name']
        }
        markers_to_add.append(rest)
    sndmap = Map(
        identifier="sndmap",
        lat=43.72,
        lng=10.40,
        markers=markers_to_add,
        zoom_control=True,
        style="height:600px;width:1000px;margin:0;",
        zoom=16
    )
    return render_template('map.html',restaurants=restaurants, sndmap=sndmap)