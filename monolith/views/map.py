from flask import Blueprint, redirect, render_template, request, make_response, flash
from monolith.database import db, Restaurant, Like, Booking, User, Table
from flask_login import current_user, login_required

map = Blueprint('map', __name__)


@map.route('/restaurants_map', methods=['GET'])
@login_required
def map_page():
    restaurants = Restaurant.query.all()
    return render_template('map.html',restaurants=restaurants)