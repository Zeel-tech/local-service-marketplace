from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
@login_required
def index():
    items = (current_user.notifications
             .order_by(Notification.created_at.desc(), Notification.id.desc())
             .limit(100).all())
    unread_ids = {n.id for n in items if not n.is_read}
    # show them as "new" on this page, then mark everything read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', items=items, unread_ids=unread_ids)
