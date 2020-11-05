from flask import Blueprint, render_template, make_response
from monolith.database import db, Restaurant, Notification
from monolith.auth import current_user
from monolith.background import log

home = Blueprint('home', __name__)


@home.route('/')
def index(): 
    """
    returns The Homepage
    """
    result = log.delay("Logging Stuff")
    print(result.wait())
    notifications = None
    if current_user is not None and hasattr(current_user, 'id'):
        restaurants = db.session.query(Restaurant).filter_by(id=current_user.rest_id)
        notifications = db.session.query(Notification).filter_by(user_notified_id=current_user.id).all()
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
