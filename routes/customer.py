from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import WorkerProfile, Booking, Review

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

        booking = Booking(
            customer_id=current_user.id,
            worker_profile_id=worker_profile.id,
            service_date=datetime.strptime(service_date, '%Y-%m-%d').date(),
            address=address,
            notes=notes,
            status='pending'
        )
        db.session.add(booking)
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
        rating = int(request.form.get('rating', 5))
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
