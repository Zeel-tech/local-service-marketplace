from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from datetime import datetime
from models import WorkerProfile, Booking, SERVICE_CATEGORIES
from notifications import notify
from uploads import save_profile_photo, delete_profile_photo

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

        photo = request.files.get('photo')
        if photo and photo.filename:
            new_name = save_profile_photo(photo)
            if new_name:
                delete_profile_photo(profile.photo_filename)
                profile.photo_filename = new_name
            else:
                flash('Photo not saved: use a JPG, PNG or WEBP image.', 'error')

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


# action -> (status the booking must currently have, new status)
BOOKING_TRANSITIONS = {
    'accept': ('pending', 'accepted'),
    'reject': ('pending', 'rejected'),
    'complete': ('accepted', 'completed'),
}
STATUS_MESSAGES = {
    'accepted': 'accepted your booking',
    'rejected': 'declined your booking request',
    'completed': 'marked your booking as completed',
}


@worker_bp.route('/booking/<int:booking_id>/<action>', methods=['POST'])
@login_required
def update_booking(booking_id, action):
    if not worker_required():
        flash('Only worker accounts can access this page.', 'error')
        return redirect(url_for('main.index'))

    booking = db.get_or_404(Booking, booking_id)

    if booking.worker_profile.user_id != current_user.id:
        flash('Not authorized.', 'error')
        return redirect(url_for('worker.dashboard'))

    if action == 'mark-paid':  # customer paid the professional in cash
        if booking.status not in ('accepted', 'completed') or booking.payment_status != 'unpaid':
            flash('This booking cannot be marked as paid.', 'error')
            return redirect(url_for('worker.dashboard'))
        booking.payment_status = 'paid'
        booking.payment_method = 'cash'
        booking.paid_at = datetime.utcnow()
        notify(booking.customer, f'{current_user.name} confirmed your cash payment of ₹{int(booking.amount or 0)}.',
               url_for('customer.my_bookings'))
        db.session.commit()
        flash('Cash payment recorded.', 'success')
        return redirect(url_for('worker.dashboard'))

    if action not in BOOKING_TRANSITIONS:
        flash('Invalid action.', 'error')
        return redirect(url_for('worker.dashboard'))

    required, new_status = BOOKING_TRANSITIONS[action]
    if booking.status != required:
        flash(f'Cannot {action} a booking that is {booking.status}.', 'error')
        return redirect(url_for('worker.dashboard'))

    booking.status = new_status
    notify(booking.customer, f'{current_user.name} {STATUS_MESSAGES[new_status]}.',
           url_for('customer.my_bookings'))
    db.session.commit()
    flash(f'Booking marked as {booking.status}.', 'success')
    return redirect(url_for('worker.dashboard'))
