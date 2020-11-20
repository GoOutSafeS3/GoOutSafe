from flask import Blueprint, render_template, make_response
from monolith.app import gateway
from monolith.auth import current_user

home = Blueprint('home', __name__)

@home.route('/')
def index():
    """
    returns The Homepage
    """
    notifications = None
    if current_user is not None and hasattr(current_user, 'id'):
        restaurants, status_rest = gateway.get_restaurant(current_user['rest_id'])
        notifications, status_noti = gateway.get_notifications(current_user['id'])
    else:
        restaurants = None
    return render_template("index.html", restaurants=restaurants, notifications=notifications)


@home.app_errorhandler(404)
def not_found_page(error):  # pragma: no cover
    """
    404 Page error
    :return: template *error.html*
    :rtype: template
    """
    return make_response(render_template('error.html', error='404'),404)


@home.app_errorhandler(401)
def permission_denied_page(error):  # pragma: no cover
    """
    401 Page error
    :return: template *error.html*
    :rtype: template
    """
    return make_response(render_template('error.html', error='401'),401)


@home.app_errorhandler(500)
def not_found_page(error):  # pragma: no cover
    """
    404 Page error
    :return: template *error.html*
    :rtype: template
    """
    return make_response(render_template('error.html', error='500'), 500)
