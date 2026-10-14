from flask import Flask
import os
import click
from sqlalchemy import inspect, text
from extensions import db, login_manager

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Columns added after the first release. db.create_all() creates new tables but never
# alters existing ones, so these are added automatically for databases made earlier.
NEW_COLUMNS = {
    'worker_profiles': {
        'photo_filename': 'VARCHAR(255)',
        'is_verified': 'BOOLEAN DEFAULT FALSE',
        'verified_at': 'TIMESTAMP',
    },
    'bookings': {
        'amount': 'FLOAT',
        'payment_status': "VARCHAR(20) DEFAULT 'unpaid'",
        'payment_method': 'VARCHAR(20)',
        'paid_at': 'TIMESTAMP',
    },
}


def upgrade_schema():
    """Create missing tables and add any missing columns to existing ones."""
    db.create_all()
    inspector = inspect(db.engine)
    with db.engine.begin() as conn:
        for table, columns in NEW_COLUMNS.items():
            existing = {c['name'] for c in inspector.get_columns(table)}
            for name, ddl in columns.items():
                if name not in existing:
                    conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {name} {ddl}'))
        # back-fill rows that pre-date the new columns
        conn.execute(text(
            'UPDATE bookings SET amount = (SELECT price_per_visit FROM worker_profiles '
            'WHERE worker_profiles.id = bookings.worker_profile_id) WHERE amount IS NULL'))
        conn.execute(text("UPDATE bookings SET payment_status = 'unpaid' WHERE payment_status IS NULL"))
        conn.execute(text('UPDATE worker_profiles SET is_verified = FALSE WHERE is_verified IS NULL'))


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:1234@localhost:5432/fixlocal'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Profile photo uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads', 'profiles')
    app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3 MB
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.auth import auth_bp
    from routes.customer import customer_bp
    from routes.worker import worker_bp
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.notifications import notifications_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)

    @app.errorhandler(413)
    def too_large(_e):
        from flask import flash, redirect, request
        flash('That file is too large (max 3 MB).', 'error')
        return redirect(request.referrer or '/')

    @app.cli.command('create-admin')
    @click.option('--email', prompt=True)
    @click.option('--name', default='Admin', show_default=True)
    @click.password_option()
    def create_admin(email, name, password):
        """Create an admin account (or promote an existing user to admin)."""
        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(name=name, email=email, role='admin')
        user.role = 'admin'
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin ready: {email}')

    with app.app_context():
        upgrade_schema()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
