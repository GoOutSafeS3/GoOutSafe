from flask import Blueprint, render_template

from monolith.database import db, Restaurant, Like
from monolith.auth import current_user


home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        restaurants = db.session.query(Restaurant)
    else:
        restaurants = None
    return render_template("index.html", restaurants=restaurants)


@home.app_errorhandler(404)
def not_found_page(error):
    """
    404 Page error
    :return: template *error.html*
    :rtype: template
    """
    return render_template('error.html', error='404')


@home.app_errorhandler(401)
def permission_denied_page(error):
    """
    401 Page error
    :return: template *error.html*
    :rtype: template
    """
    return render_template('error.html', error='401')
