from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'worker'
    city = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    worker_profile = db.relationship('WorkerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    bookings_made = db.relationship('Booking', foreign_keys='Booking.customer_id', backref='customer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class WorkerProfile(db.Model):
    __tablename__ = 'worker_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)  # plumber, electrician, etc.
    description = db.Column(db.Text)
    price_per_visit = db.Column(db.Float, nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)

    bookings = db.relationship('Booking', backref='worker_profile', lazy='dynamic')
    reviews = db.relationship('Review', backref='worker_profile', lazy='dynamic')

    @property
    def avg_rating(self):
        revs = self.reviews.all()
        if not revs:
            return 0
        return round(sum(r.rating for r in revs) / len(revs), 1)

    @property
    def review_count(self):
        return self.reviews.count()


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    worker_profile_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    review = db.relationship('Review', backref='booking', uselist=False, cascade='all, delete-orphan')


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, unique=True)
    worker_profile_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


SERVICE_CATEGORIES = [
    'Plumber', 'Electrician', 'Carpenter', 'Mechanic',
    'Driver', 'Painter', 'Cleaner', 'Technician', 'Cook'
]
