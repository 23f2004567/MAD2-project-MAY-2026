# 🏔️ PeakPath
### *Explore. Book. Trek.*

PeakPath is a full-stack role-based trekking management platform built as an academic project. It supports three roles — **Admin**, **Trek Staff**, and **User/Trekker** — each with a dedicated dashboard and strictly enforced backend authorization.

---

## ✨ Features

| Role | Capabilities |
|------|-------------|
| **Admin** | Manage treks, staff, users, bookings; view analytics reports |
| **Trek Staff** | Manage assigned treks, update status/slots, view & mark participants |
| **User/Trekker** | Browse/search/filter treks, book, cancel, view history, export CSV |

**Platform features:**
- JWT-based secure authentication
- Redis caching for trek listings and dashboard stats (5-min TTL + invalidation)
- Celery async CSV export (user-triggered)
- Celery Beat: daily trek reminders + monthly admin HTML email report
- SQLite database created **programmatically** — no manual setup required
- Bootstrap 5 responsive UI

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3, Flask-SQLAlchemy, Flask-JWT-Extended |
| Database | SQLite (programmatically created) |
| Cache | Redis |
| Task Queue | Celery 5 with Redis as broker & result backend |
| Frontend | Vue 3, Vue Router 4, Axios, Chart.js |
| Styling | Bootstrap 5, custom CSS |

---

## 📁 Project Structure

```
Peak Path/
├── backend/
│   ├── models/          # User, Trek, Booking SQLAlchemy models
│   ├── routes/          # auth, admin, staff, user, common blueprints
│   ├── tasks/           # Celery tasks (CSV export, reminders, report)
│   ├── exports/         # Generated CSV files (auto-created)
│   ├── app.py           # Flask application factory
│   ├── config.py        # All configuration
│   ├── extensions.py    # db, jwt, celery singletons
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── assets/      # Global CSS
│   │   ├── components/  # Reusable Vue components
│   │   ├── views/       # admin/, staff/, user/, auth/ pages
│   │   ├── router/      # Vue Router with role guards
│   │   └── services/    # Axios API client
│   └── package.json
│
└── README.md
```

---

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **Redis** (see setup below)

---

## ⚙️ Setup Instructions

### 1. Redis Setup (Windows)

**Option A — WSL2 (Recommended):**
```bash
# In WSL2 terminal:
sudo apt-get install redis-server
sudo service redis-server start
redis-cli ping   # Should return PONG
```

**Option B — Memurai (Windows native Redis-compatible):**
Download from https://www.memurai.com/ and install. It runs as a Windows service automatically.

**Option C — Docker:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

---

### 2. Backend Setup

```bash
cd "d:\Peak Path\backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1    # PowerShell
# OR
.\venv\Scripts\activate.bat    # CMD

# Install dependencies (already done if following setup order)
pip install -r requirements.txt

# The database is created automatically when you run the app.
# No manual table creation required.
```

**Default Admin Credentials** (seeded automatically):
```
Email:    admin@peakpath.com
Password: Admin@123
```

**Demo Staff Credentials:**
```
Email:    rajan@peakpath.com   Password: Staff@123
Email:    meena@peakpath.com   Password: Staff@123
```

**Demo User Credentials:**
```
Email:    arjun@example.com    Password: User@123
```

---

### 3. Frontend Setup

```bash
cd "d:\Peak Path\frontend"
npm install     # Already done during project setup
```

---

## 🚀 Running the Application

Open **5 separate terminals** for the full stack:

### Terminal 1 — Redis
```bash
# WSL2:
sudo service redis-server start

# OR if using Memurai: it starts automatically as a service
# Verify: redis-cli ping  → should return PONG
```

### Terminal 2 — Flask Backend
```bash
cd "d:\Peak Path\backend"
.\venv\Scripts\Activate.ps1
python app.py
# Runs on http://localhost:5000
```

### Terminal 3 — Vue Frontend
```bash
cd "d:\Peak Path\frontend"
npm run dev
# Runs on http://localhost:5173
```

### Terminal 4 — Celery Worker
```bash
cd "d:\Peak Path\backend"
.\venv\Scripts\Activate.ps1

# --pool=solo is required on Windows (prefork pool not supported)
.\venv\Scripts\celery -A app.celery worker --loglevel=info --pool=solo
```

### Terminal 5 — Celery Beat (Scheduler)
```bash
cd "d:\Peak Path\backend"
.\venv\Scripts\Activate.ps1

.\venv\Scripts\celery -A app.celery beat --loglevel=info
```

---

## 🧪 Testing Key Features

### Test CSV Export (Async Celery Task)
1. Log in as a User (e.g., `arjun@example.com`)
2. Go to **History** page
3. Click **Export History CSV**
4. The task is queued in Celery — status is polled every 2 seconds
5. When ready, a **Download CSV** button appears
6. CSV file is in `backend/exports/`

### Test Daily Reminders (Manual Trigger)
```bash
cd "d:\Peak Path\backend"
.\venv\Scripts\Activate.ps1

# Start local SMTP debug server first:
python -m smtpd -n -c DebuggingServer localhost:1025

# In another terminal, trigger the task manually:
.\venv\Scripts\python -c "
from app import create_app
app = create_app()
with app.app_context():
    from tasks.celery_tasks import send_daily_trek_reminders
    send_daily_trek_reminders.delay()
print('Task queued')
"
```

### Test Monthly Report (Manual Trigger)
```bash
.\venv\Scripts\python -c "
from app import create_app
app = create_app()
with app.app_context():
    from tasks.celery_tasks import send_monthly_admin_report
    send_monthly_admin_report.delay()
print('Task queued')
"
```

---

## 🌐 Application URLs

| URL | Description |
|-----|-------------|
| http://localhost:5173/ | PeakPath Login Page |
| http://localhost:5173/register | User Registration |
| http://localhost:5173/admin/dashboard | Admin Dashboard |
| http://localhost:5173/staff/dashboard | Staff Dashboard |
| http://localhost:5173/dashboard | User Dashboard |
| http://localhost:5000/api/treks | Flask API (public trek listing) |

---

## 🔑 Environment Variables (Optional)

Create `backend/.env` to override defaults:

```env
SECRET_KEY=your-flask-secret
JWT_SECRET_KEY=your-jwt-secret
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
MAIL_SERVER=localhost
MAIL_PORT=1025
ADMIN_EMAIL=admin@peakpath.com
FLASK_DEBUG=true
```

---

## 🔒 Security Notes

- Passwords are hashed using Werkzeug's bcrypt-based `generate_password_hash`
- JWT tokens expire after 8 hours
- Backend enforces role-based authorization on **every** protected endpoint
- Staff can only access treks where `trek.assigned_staff_id == current_staff.id`
- Admin cannot be self-registered (seeded programmatically only)
- Staff cannot self-register (Admin creates staff accounts)

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `redis.exceptions.ConnectionError` | Ensure Redis is running (`redis-cli ping`) |
| Celery worker not processing tasks | Check `--pool=solo` flag on Windows |
| `ModuleNotFoundError` | Activate virtualenv: `.\venv\Scripts\Activate.ps1` |
| CORS errors | Ensure Flask runs on port 5000 and Vite proxy is active |
| Port 5173 already in use | Change port in `vite.config.js` |
| Database not found | Run `python app.py` once — it creates `peakpath.db` automatically |
| Frontend shows blank page | Check browser console; ensure `npm run dev` is running |

---

## 📅 Celery Beat Schedule

| Task | Schedule |
|------|----------|
| Daily Trek Reminders | Every day at 08:00 UTC |
| Monthly Admin Report | 1st of each month at 07:00 UTC |

---

*PeakPath — Explore. Book. Trek. | Academic Project — Flask + Vue.js*
