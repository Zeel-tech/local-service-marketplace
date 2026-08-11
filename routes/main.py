from flask import Blueprint, render_template, request
from models import WorkerProfile, SERVICE_CATEGORIES

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html', categories=SERVICE_CATEGORIES)


@main_bp.route('/browse')
def browse():
    category = request.args.get('category', '')
    city = request.args.get('city', '')

    query = WorkerProfile.query.filter_by(is_available=True)
    if category:
        query = query.filter_by(category=category)

    workers = query.all()

    if city:
        workers = [w for w in workers if w.user.city and city.lower() in w.user.city.lower()]

    return render_template('browse.html', workers=workers, categories=SERVICE_CATEGORIES,
                            selected_category=category, selected_city=city)
