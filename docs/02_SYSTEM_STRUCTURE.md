# FixLocal — System Structure

## 1. Tech Stack
| Layer | Choice | Why |
|---|---|---|
| Backend | Flask (Python) | You already know Python; lightweight, fast to build in 4 days |
| Auth | Flask-Login | Handles sessions, `@login_required`, current_user — minimal boilerplate |
| ORM / DB | Flask-SQLAlchemy + SQLite | You know SQL; SQLAlchemy maps it to Python objects; SQLite needs zero setup |
| Frontend | Jinja2 templates + vanilla CSS/JS | No build step, no npm — fewer moving parts to break before submission |

## 2. Folder Structure
```
local-service-marketplace/
├── app.py              # App factory — creates Flask app, registers blueprints, creates DB
├── models.py            # All database models (User, WorkerProfile, Booking, Review)
├── requirements.txt      # Python dependencies
├── routes/               # Route logic, split by responsibility (Blueprints)
│   ├── auth.py            # signup, login, logout
│   ├── main.py             # homepage, browse/search
│   ├── worker.py           # worker profile + dashboard + booking actions
│   └── customer.py         # booking creation, booking history, reviews
├── templates/             # HTML (Jinja2) — one folder per role for clarity
│   ├── base.html            # shared layout (header/nav/footer)
│   ├── index.html
│   ├── browse.html
│   ├── auth/
│   ├── worker/
│   └── customer/
└── static/css/style.css   # Design system
```

**Why Blueprints?** Instead of one giant `app.py` with every route, routes are split by who uses them (auth / worker / customer / main). This is a standard Flask pattern and makes it easy to explain in a viva: *"my customer routes and worker routes are isolated, so a bug in one doesn't touch the other."*

## 3. Entity-Relationship Model

**Entities:**
- **User** — one row per person, `role` field distinguishes customer vs worker
- **WorkerProfile** — 1-to-1 with a User where `role='worker'`
- **Booking** — links a customer (User) to a WorkerProfile
- **Review** — 1-to-1 with a completed Booking

**Relationships:**
- One User (worker) → One WorkerProfile
- One WorkerProfile → Many Bookings
- One User (customer) → Many Bookings
- One Booking → One Review (only after completion)

## 4. Request Flow Example (Booking a worker)
1. Customer clicks "Book Now" on a worker's ticket card → `GET /customer/book/<worker_id>`
2. Form submitted → `POST /customer/book/<worker_id>` → creates `Booking` row with `status='pending'`
3. Worker sees it on `/worker/dashboard` → clicks Accept → `GET /worker/booking/<id>/accept` → status becomes `accepted`
4. Worker clicks Mark Completed → status becomes `completed`
5. Customer sees "Leave Review" button only when `status == 'completed'` → submits → `Review` row created, linked to that booking

This request-flow narrative is good material for your viva — walk through it exactly like this when asked "explain how booking works."
