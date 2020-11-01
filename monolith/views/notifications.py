from monolith.utilities.notification import delete_notification
from flask import Blueprint, redirect, render_template, request, flash, make_response, current_app
from flask_login import login_required, current_user
from monolith.database import db, Notification, User


notifications_page = Blueprint('notifications_page', __name__)


@notifications_page.route('/notifications', methods=['GET'])
@login_required
def list_notifications():
    if current_user is not None and hasattr(current_user, 'id'):
        notifications = db.session.query(Notification).filter_by(user_notified_id=current_user.id).all()
    return render_template("notifications.html", notifications=notifications, title="Notifications")


@notifications_page.route('/<int:pos_id>/mark_as_read', methods=['GET','POST'])
@login_required
def mark_as_read(pos_id):
    if current_user is not None and hasattr(current_user, 'id'):
        notifications = db.session.query(Notification).filter_by(user_notified_id=current_user.id).all()
        if pos_id is None:
            return make_response(render_template("index.html",notifications=notifications),400)
        delete_notification(pos_id, current_user.id)
    return render_template("index.html", notifications=notifications)

