# FixLocal — Feature List

## 1. User Management
| Feature | Description | Status |
|---|---|---|
| Dual-role signup | Users register as either **Customer** or **Worker** | ✅ Built |
| Login / Logout | Session-based auth using Flask-Login | ✅ Built |
| Password security | Passwords hashed with Werkzeug (never stored plain) | ✅ Built |
| Role-based access control | Customer-only and worker-only routes are protected | ✅ Built |

## 2. Worker Features
| Feature | Description | Status |
|---|---|---|
| Profile setup | Category, description, price/visit, years of experience | ✅ Built |
| Profile editing | Worker can update profile anytime | ✅ Built |
| Job dashboard | View all incoming booking requests | ✅ Built |
| Accept / Reject booking | Worker decides on pending requests | ✅ Built |
| Mark job completed | Worker closes out an accepted job | ✅ Built |
| Rating visibility | Average rating + review count shown on profile | ✅ Built |

## 3. Customer Features
| Feature | Description | Status |
|---|---|---|
| Browse professionals | Grid view of all available workers | ✅ Built |
| Filter by category | 9 categories (Plumber, Electrician, etc.) | ✅ Built |
| Filter by city | Text-based city search | ✅ Built |
| Book a worker | Choose date, address, notes | ✅ Built |
| Booking history | Track status of every booking made | ✅ Built |
| Leave a review | Rate 1–5 stars + comment, only after job is completed | ✅ Built |

## 4. Booking Lifecycle
```
   pending  ──accept──▶  accepted  ──complete──▶  completed  ──review──▶ reviewed
      │
      └──reject──▶  rejected
```

## 5. Added in Phase 2 (all ✅ Built)
| Feature | How it works |
|---|---|
| Worker profile photo upload | Worker uploads JPG/PNG/WEBP (max 3 MB) on the profile page. File type is checked by its real bytes, saved under a random name in `static/uploads/profiles/`. Browse cards fall back to an initial-letter avatar. |
| Admin panel (verify workers) | `/admin` shows stats and a review queue. Admin clicks **Verify** → worker gets a green ✓ Verified badge, is listed first on Browse, and is notified. Can be reversed. Admin accounts cannot be created through signup. |
| Search by price range | Browse has Min ₹ / Max ₹ fields plus a "Verified only" checkbox, all combined with category and city. |
| Notifications | In-app bell with unread count + `/notifications` page, and e-mail when SMTP is configured (otherwise logged to console). Triggered by: new booking, accept/reject/complete, cancellation, payment, and verification. |
| Payment status (mock) | Each booking stores amount, `payment_status` (unpaid / paid / refunded), method and time. Customer pays by UPI/Card on a demo page, or worker taps **Cash Received**. No real gateway. |
| Cancel booking | Customer can cancel while pending or accepted. A paid booking becomes *refunded* (mock). Worker is notified. |

## 6. Hardening done along the way
- Booking status changes are now **POST-only** and validated (pending → accepted/rejected, accepted → completed). Previously any link click could jump states.
- Signup role is whitelisted to customer/worker.
- Service date cannot be in the past; review rating is clamped to 1–5.
- The app auto-adds the new columns to an existing database on start (`upgrade_schema()` in `app.py`), so no manual migration is needed.
