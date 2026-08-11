from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import WorkerProfile, Booking, SERVICE_CATEGORIES

worker_bp = Blueprint('worker', __name__, url_prefix='/worker')


def worker_required():
    return current_user.is_authenticated and current_user.role == 'worker'


@worker_bp.route('/setup-profile', methods=['GET', 'POST'])
@login_required
def setup_profile():
    if not worker_required():
        flash('Only worker accounts can access this page.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        category = request.form.get('category')
        description = request.form.get('description', '').strip()
        price = request.form.get('price_per_visit', 0)
        experience = request.form.get('experience_years', 0)

        profile = current_user.worker_profile
        if profile is None:
            profile = WorkerProfile(user_id=current_user.id)
            db.session.add(profile)

        profile.category = category
        profile.description = description
        profile.price_per_visit = float(price) if price else 0
        profile.experience_years = int(experience) if experience else 0

        db.session.commit()
        flash('Profile saved!', 'success')
        return redirect(url_for('worker.dashboard'))

    return render_template('worker/setup_profile.html', categories=SERVICE_CATEGORIES,
                            profile=current_user.worker_profile)


@worker_bp.route('/dashboard')
@login_required
def dashboard():
    if not worker_required():
        flash('Only worker accounts can access this page.', 'error')
        return redirect(url_for('main.index'))

    if current_user.worker_profile is None:
        return redirect(url_for('worker.setup_profile'))

    bookings = current_user.worker_profile.bookings.order_by(Booking.created_at.desc()).all()
    return render_template('worker/dashboard.html', bookings=bookings, profile=current_user.worker_profile)


@worker_bp.route('/booking/<int:booking_id>/<action>')
@login_required
def update_booking(booking_id, action):
    if not worker_required():
        flash('Only worker accounts can access this page.', 'error')
        return redirect(url_for('main.index'))

    booking = Booking.query.get_or_404(booking_id)

    if booking.worker_profile.user_id != current_user.id:
        flash('Not authorized.', 'error')
        return redirect(url_for('worker.dashboard'))

    if action == 'accept':
        booking.status = 'accepted'
    elif action == 'reject':
        booking.status = 'rejected'
    elif action == 'complete':
        booking.status = 'completed'
    else:
        flash('Invalid action.', 'error')
        return redirect(url_for('worker.dashboard'))

    db.session.commit()
    flash(f'Booking marked as {booking.status}.', 'success')
    return redirect(url_for('worker.dashboard'))
