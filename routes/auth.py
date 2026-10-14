from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        role = request.form.get('role', 'customer')
        if role not in ('customer', 'worker'):  # never allow self-signup as admin
            role = 'customer'

        if not name or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('auth.signup'))

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('auth.signup'))

        user = User(name=name, email=email, phone=phone, city=city, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)

        if role == 'worker':
            return redirect(url_for('worker.setup_profile'))
        return redirect(url_for('main.index'))

    return render_template('auth/signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
