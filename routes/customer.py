from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import WorkerProfile, Booking, Review, PAYMENT_METHODS
from notifications import notify

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')


def customer_required():
    return current_user.is_authenticated and current_user.role == 'customer'


@customer_bp.route('/book/<int:worker_id>', methods=['GET', 'POST'])
@login_required
def book_worker(worker_id):
    if not customer_required():
        flash('Only customer accounts can book services.', 'error')
        return redirect(url_for('main.index'))

    worker_profile = WorkerProfile.query.get_or_404(worker_id)

    if request.method == 'POST':
        service_date = request.form.get('service_date')
        address = request.form.get('address', '').strip()
        notes = request.form.get('notes', '').strip()

        if not service_date or not address:
            flash('Please fill in date and address.', 'error')
            return redirect(url_for('customer.book_worker', worker_id=worker_id))

        try:
            parsed_date = datetime.strptime(service_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Please choose a valid date.', 'error')
            return redirect(url_for('customer.book_worker', worker_id=worker_id))
        if parsed_date < date.today():
            flash('Service date cannot be in the past.', 'error')
            return redirect(url_for('customer.book_worker', worker_id=worker_id))

        booking = Booking(
            customer_id=current_user.id,
            worker_profile_id=worker_profile.id,
            service_date=parsed_date,
            address=address,
            notes=notes,
            status='pending',
            amount=worker_profile.price_per_visit,
            payment_status='unpaid'
        )
        db.session.add(booking)
        notify(worker_profile.user,
               f'New booking request from {current_user.name} for {parsed_date.strftime("%d %b %Y")}.',
               url_for('worker.dashboard'))
        db.session.commit()
        flash('Booking request sent!', 'success')
        return redirect(url_for('customer.my_bookings'))

    return render_template('customer/book.html', worker_profile=worker_profile)


@customer_bp.route('/my-bookings')
@login_required
def my_bookings():
    if not customer_required():
        flash('Only customer accounts can access this page.', 'error')
        return redirect(url_for('main.index'))

    bookings = current_user.bookings_made.order_by(Booking.created_at.desc()).all()
    return render_template('customer/my_bookings.html', bookings=bookings)


@customer_bp.route('/review/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def leave_review(booking_id):
    if not customer_required():
        flash('Only customer accounts can leave reviews.', 'error')
        return redirect(url_for('main.index'))

    booking = Booking.query.get_or_404(booking_id)

    if booking.customer_id != current_user.id:
        flash('Not authorized.', 'error')
        return redirect(url_for('customer.my_bookings'))

    if booking.status != 'completed':
        flash('You can only review completed bookings.', 'error')
        return redirect(url_for('customer.my_bookings'))

    if booking.review is not None:
        flash('You already reviewed this booking.', 'error')
        return redirect(url_for('customer.my_bookings'))

    if request.method == 'POST':
        try:
            rating = min(5, max(1, int(request.form.get('rating', 5))))
        except ValueError:
            rating = 5
        comment = request.form.get('comment', '').strip()

        review = Review(
            booking_id=booking.id,
            worker_profile_id=booking.worker_profile_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        flash('Review submitted!', 'success')
        return redirect(url_for('customer.my_bookings'))

    return render_template('customer/review.html', booking=booking)


def _own_booking_or_none(booking_id):
    booking = db.get_or_404(Booking, booking_id)
    if booking.customer_id != current_user.id:
        flash('Not authorized.', 'error')
        return None
    return booking


@customer_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    if not customer_required():
        flash('Only customer accounts can cancel bookings.', 'error')
        return redirect(url_for('main.index'))

    booking = _own_booking_or_none(booking_id)
    if booking is None:
        return redirect(url_for('customer.my_bookings'))

    if booking.status not in ('pending', 'accepted'):
        flash(f'A {booking.status} booking can no longer be cancelled.', 'error')
        return redirect(url_for('customer.my_bookings'))

    booking.status = 'cancelled'
    msg = f'{current_user.name} cancelled their booking for {booking.service_date.strftime("%d %b %Y")}.'
    if booking.payment_status == 'paid':
        booking.payment_status = 'refunded'  # mock refund
        flash('Booking cancelled. Your payment is marked as refunded.', 'success')
    else:
        flash('Booking cancelled.', 'success')
    notify(booking.worker_profile.user, msg, url_for('worker.dashboard'))
    db.session.commit()
    return redirect(url_for('customer.my_bookings'))


@customer_bp.route('/booking/<int:booking_id>/pay', methods=['GET', 'POST'])
@login_required
def pay_booking(booking_id):
    """Mock payment: no real gateway, it only records that the customer paid."""
    if not customer_required():
        flash('Only customer accounts can pay for bookings.', 'error')
        return redirect(url_for('main.index'))

    booking = _own_booking_or_none(booking_id)
    if booking is None:
        return redirect(url_for('customer.my_bookings'))

    if booking.status not in ('accepted', 'completed') or booking.payment_status != 'unpaid':
        flash('This booking cannot be paid right now (it must be accepted and unpaid).', 'error')
        return redirect(url_for('customer.my_bookings'))

    if request.method == 'POST':
        method = request.form.get('method')
        if method not in ('upi', 'card'):
            flash('Choose UPI or Card. For cash, pay the professional directly.', 'error')
            return redirect(url_for('customer.pay_booking', booking_id=booking.id))
        booking.payment_status = 'paid'
        booking.payment_method = method
        booking.paid_at = datetime.utcnow()
        notify(booking.worker_profile.user,
               f'{current_user.name} paid ₹{int(booking.amount or 0)} via {PAYMENT_METHODS[method]}.',
               url_for('worker.dashboard'))
        db.session.commit()
        flash('Payment recorded (demo mode — no real money moved).', 'success')
        return redirect(url_for('customer.my_bookings'))

    return render_template('customer/pay.html', booking=booking)
