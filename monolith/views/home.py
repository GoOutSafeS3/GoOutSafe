from flask import Blueprint, render_template, make_response
from monolith.gateway import get_getaway
from flask_login import current_user

home = Blueprint('home', __name__)

@home.route('/')
def index():
    """
    returns The Homepage
    """
    notifications = None
    restaurants = None
    import sys
    print(current_user.is_authenticated, file=sys.stderr)
    print(current_user, file=sys.stderr)
    if current_user is not None and hasattr(current_user, 'id'):
        if current_user.rest_id is not None:
            restaurant, status_rest = get_getaway().get_restaurant(current_user.rest_id)
            restaurants = [restaurant]
        notifications, status_noti = get_getaway().get_notifications(current_user.id)
    return render_template("index.html",current_user=current_user, restaurants=restaurants, notifications=notifications)


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
