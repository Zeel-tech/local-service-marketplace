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

## 5. Not Yet Built (candidates for Day 2–4)
| Feature | Why it's valuable | Effort |
|---|---|---|
| Worker profile photo upload | Makes browse page look real | Low |
| Admin panel (verify workers) | Matches "verified professionals" pitch directly | Medium |
| Search by price range | Better filtering | Low |
| Email/SMS notification on booking status change | Realistic UX touch | Medium |
| Payment status field (mock, no real gateway) | Addresses "unorganized payment" problem from your brief | Low–Medium |
| Cancel booking (by customer) | Currently customers can't cancel once sent | Low |

Decide with your teammate/mentor which 1–2 of these to add — don't try all of them in 4 days.
