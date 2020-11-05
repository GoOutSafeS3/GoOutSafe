from monolith.utilities.notification import delete_notification
from flask import Blueprint, redirect, render_template, request, flash, make_response, current_app
from flask_login import login_required, current_user
from monolith.database import db, Notification, User, Restaurant


notifications_page = Blueprint('notifications_page', __name__)


@notifications_page.route('/notifications', methods=['GET'])
@login_required
def list_notifications(): # pragma: no cover
    """
    Shows a page with notifications for the current use

    You must logged as customer or operator

    Error status codes:
        404 -- If a user other than customer tries to view it
    """

    if current_user is not None and hasattr(current_user, 'id'):
        if current_user.is_admin or current_user.is_health_authority:
            return make_response(render_template('error.html', error='404'), 404)
        notifications = db.session.query(Notification).filter_by(user_notified_id=current_user.id).all()
    return render_template("notifications.html", notifications=notifications, title="Notifications")


@notifications_page.route('/notifications/<int:notification_id>/mark_as_read', methods=['GET','POST'])
@login_required
def mark_as_read(notification_id): # pragma: no cover
    """
        Mark as read the notification with id equal to notification_id

        You must logged as customer or operator,
        the notification must be addressed to the logged in user

        Error status codes:
            404 -- If a user other than customer or operator tries to view it
            401 -- If a user try to mark as read a notification addressed to an other user
        """
    notification_with_id = Notification.query.filter_by(notification_id=notification_id).first()
    if notification_with_id is None:
        return make_response(render_template('error.html', error='404'), 404)
    if current_user is not None and hasattr(current_user, 'id'):
        if current_user.is_admin or current_user.is_health_authority:
            return make_response(render_template('error.html', error='404'), 401)
        if notification_with_id.user_notified_id != current_user.id:
            return make_response(render_template('error.html', error='401'), 401)
        restaurants = db.session.query(Restaurant).filter_by(id=current_user.rest_id)
        notifications = Notification.query.filter_by(user_notified_id=current_user.id).all()
        if not delete_notification(notification_id):
            return make_response(render_template("index.html",notifications=notifications),404)
    return render_template("index.html", notifications=notifications, restaurants=restaurants)

