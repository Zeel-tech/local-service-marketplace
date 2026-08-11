# FixLocal — Local Service Marketplace

A web platform that connects customers with verified local service professionals (plumbers, electricians, carpenters, mechanics, cleaners, cooks, and more) — solving the problem of unorganized, untrustworthy local service discovery.

## Problem it solves
- No trusted platform to find verified local workers
- Hard to compare prices and service quality
- Booking is unorganized (usually just phone calls)
- No record of service/booking history
- Skilled workers have no online visibility

## Features
- **Dual role auth** — separate signup/login flows for Customers and Workers
- **Worker profiles** — category, price per visit, experience, description
- **Browse & filter** — search professionals by service category and city
- **Booking system** — request → pending → accepted/rejected → completed, fully tracked
- **Reviews & ratings** — customers rate completed bookings only (prevents fake reviews)
- **Role-based dashboards** — workers manage incoming jobs, customers track their bookings

## Tech Stack
- **Backend:** Python, Flask, Flask-Login (session auth), Flask-SQLAlchemy (ORM)
- **Database:** SQLite
- **Frontend:** Jinja2 templates, vanilla HTML/CSS/JS (no framework — kept dependency-free)
- **Security:** Password hashing via Werkzeug, login-protected routes, role-based access control

## Project Structure
```
local-service-marketplace/
├── app.py                 # App factory, config, blueprint registration
├── models.py               # User, WorkerProfile, Booking, Review models
├── requirements.txt
├── routes/
│   ├── auth.py             # signup, login, logout
│   ├── main.py              # homepage, browse/search
│   ├── worker.py            # profile setup, dashboard, accept/reject/complete
│   └── customer.py          # booking, my bookings, reviews
├── templates/               # Jinja2 HTML templates
└── static/css/style.css     # Design system
```

## Setup & Run Locally

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser. The SQLite database (`marketplace.db`) is created automatically on first run inside an `instance/` folder.

## How to Demo It
1. Sign up as a **Worker** → fill in category, price, experience → land on dashboard
2. Log out, sign up as a **Customer**
3. Go to **Browse Services** → filter by category/city → book the worker
4. Log back in as the Worker → Accept the booking → Mark it Completed
5. Log back in as the Customer → Leave a review → see the rating reflect on the Browse page

## Possible Future Enhancements
(good talking points for a viva/interview — mention what you'd add next)
- Payment gateway integration (Razorpay/Stripe)
- Real-time notifications (booking status changes)
- Image uploads for worker portfolios and profile photos
- Admin panel for verifying workers (ID/certification upload)
- Geolocation-based search instead of text city matching
- Chat between customer and worker

## Resume Bullet Points (ready to use)

> **FixLocal — Local Service Marketplace** | Flask, SQLAlchemy, SQLite, HTML/CSS/JS
> - Built a full-stack marketplace connecting customers with verified local service professionals across 9 service categories, with role-based authentication for customers and workers
> - Designed a relational schema (Users, Worker Profiles, Bookings, Reviews) and implemented a complete booking lifecycle (pending → accepted/rejected → completed) with status tracking
> - Implemented a review system restricted to completed bookings to prevent fake ratings, with real-time average rating calculation
> - Built role-based dashboards and access control using Flask-Login, protecting routes by authentication and user role
