from flask import Blueprint, render_template, request
from models import WorkerProfile, SERVICE_CATEGORIES

main_bp = Blueprint('main', __name__)


def _to_float(value):
    try:
        return float(value) if value not in (None, '') else None
    except ValueError:
        return None


@main_bp.route('/')
def index():
    return render_template('index.html', categories=SERVICE_CATEGORIES)


@main_bp.route('/browse')
def browse():
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    min_price = _to_float(request.args.get('min_price'))
    max_price = _to_float(request.args.get('max_price'))
    verified_only = request.args.get('verified') == '1'

    query = WorkerProfile.query.filter_by(is_available=True)
    if category:
        query = query.filter_by(category=category)
    if min_price is not None:
        query = query.filter(WorkerProfile.price_per_visit >= min_price)
    if max_price is not None:
        query = query.filter(WorkerProfile.price_per_visit <= max_price)
    if verified_only:
        query = query.filter(WorkerProfile.is_verified.is_(True))

    workers = query.order_by(WorkerProfile.is_verified.desc(), WorkerProfile.price_per_visit).all()

    if city:
        workers = [w for w in workers if w.user.city and city.lower() in w.user.city.lower()]

    return render_template('browse.html', workers=workers, categories=SERVICE_CATEGORIES,
                           selected_category=category, selected_city=city,
                           min_price=request.args.get('min_price', ''),
                           max_price=request.args.get('max_price', ''),
                           verified_only=verified_only)
