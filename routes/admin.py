from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User, WorkerProfile, Booking
from notifications import notify

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access only.', 'error')
            return redirect(url_for('main.index'))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route('/')
@admin_required
def dashboard():
    flt = request.args.get('filter', 'unverified')
    query = WorkerProfile.query.join(User, WorkerProfile.user_id == User.id)
    if flt == 'unverified':
        query = query.filter(WorkerProfile.is_verified.is_(False))
    elif flt == 'verified':
        query = query.filter(WorkerProfile.is_verified.is_(True))
    workers = query.order_by(User.created_at.desc()).all()

    stats = {
        'workers': WorkerProfile.query.count(),
        'verified': WorkerProfile.query.filter_by(is_verified=True).count(),
        'customers': User.query.filter_by(role='customer').count(),
        'bookings': Booking.query.count(),
    }
    stats['unverified'] = stats['workers'] - stats['verified']
    return render_template('admin/dashboard.html', workers=workers, stats=stats, flt=flt)


@admin_bp.route('/worker/<int:profile_id>/<action>', methods=['POST'])
@admin_required
def verify_worker(profile_id, action):
    profile = db.get_or_404(WorkerProfile, profile_id)
    if action == 'verify':
        profile.is_verified = True
        profile.verified_at = datetime.utcnow()
        notify(profile.user, 'Congratulations! Your profile is now verified by FixLocal.',
               url_for('worker.dashboard'))
        flash(f'{profile.user.name} is now verified.', 'success')
    elif action == 'unverify':
        profile.is_verified = False
        profile.verified_at = None
        flash(f'Verification removed for {profile.user.name}.', 'success')
    else:
        flash('Invalid action.', 'error')
        return redirect(url_for('admin.dashboard'))
    db.session.commit()
    return redirect(request.referrer or url_for('admin.dashboard'))
