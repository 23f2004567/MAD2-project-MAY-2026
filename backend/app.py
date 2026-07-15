"""
app.py — Flask application factory.

Responsibilities:
1. Create the Flask app with all extensions.
2. Register all Blueprints.
3. Initialize the SQLite database and create tables programmatically.
4. Seed the initial Admin account if it doesn't exist.
5. Configure Celery with the app context.

Run with:
    python app.py
or via Flask CLI:
    flask run
"""

import os
from datetime import date, timedelta
from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, jwt, celery


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Celery configuration (bind to Flask app context)
    _configure_celery(app)

    # Register Blueprints
    from routes.auth   import auth_bp
    from routes.common import common_bp
    from routes.admin  import admin_bp
    from routes.staff  import staff_bp
    from routes.user   import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(user_bp)

    # Database init (creates tables programmatically)
    with app.app_context():
        # Import models so SQLAlchemy discovers them before create_all()
        from models import User, Trek, Booking
        db.create_all()
        _seed_admin(app)
        _seed_demo_data(app)

    # Ensure the CSV export directory exists
    os.makedirs(app.config["EXPORT_DIR"], exist_ok=True)

    return app


def _configure_celery(app: Flask):
    """
    Bind the Celery instance to the Flask app so tasks have access to
    the application context (db queries, config, etc.).
    """
    celery.conf.update(
        broker_url           = app.config["CELERY_BROKER_URL"],
        result_backend       = app.config["CELERY_RESULT_BACKEND"],
        task_serializer      = "json",
        result_serializer    = "json",
        accept_content       = ["json"],
        timezone             = "UTC",
        enable_utc           = True,
        # Celery Beat schedule
        beat_schedule        = {
            # Every day at 08:00 UTC
            "daily-trek-reminders": {
                "task":     "tasks.celery_tasks.send_daily_trek_reminders",
                "schedule": _crontab(hour=8, minute=0),
            },
            # 1st of each month at 07:00 UTC
            "monthly-admin-report": {
                "task":     "tasks.celery_tasks.send_monthly_admin_report",
                "schedule": _crontab(hour=7, minute=0, day_of_month=1),
            },
        },
    )

    # Make tasks run within Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def _crontab(**kwargs):
    """Return a Celery crontab schedule."""
    from celery.schedules import crontab
    return crontab(**kwargs)


def _seed_admin(app: Flask):
    """
    Create the single Admin account if it doesn't already exist.
    Admin cannot self-register — this is the only way to create one.
    Default credentials are documented in the README.
    """
    from models import User

    admin_email    = "admin@peakpath.com"
    admin_password = "Admin@123"

    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            name  = "PeakPath Admin",
            email = admin_email,
            phone = "+91-9000000000",
            role  = "admin",
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"[PeakPath] Admin seeded: {admin_email} / {admin_password}")


def _seed_demo_data(app: Flask):
    """
    Seed realistic demo treks, staff, users, and bookings so the
    application has meaningful data for an academic demonstration.
    Only runs when there are no treks yet.
    """
    from models import User, Trek, Booking

    if User.query.filter_by(email="rajan@peakpath.com").first():
        return  # Already seeded

    # Re-initialize DB to a clean demo state if the demo data is missing
    db.drop_all()
    db.create_all()
    _seed_admin(app)

    today = date.today()

    # Demo Staff
    staff1 = User(name="Rajan Sharma", email="rajan@peakpath.com", phone="+91-9100000001", role="staff")
    staff1.set_password("Staff@123")
    staff2 = User(name="Meena Nair", email="meena@peakpath.com", phone="+91-9100000002", role="staff")
    staff2.set_password("Staff@123")
    db.session.add_all([staff1, staff2])
    db.session.flush()  # Get IDs before using them in Trek

    # Demo Treks
    treks_data = [
        {
            "name": "Valley of Flowers Trek", "location": "Uttarakhand, India",
            "difficulty": "Easy", "duration_days": 6, "total_slots": 30,
            "status": "Open", "start_date": today + timedelta(days=20),
            "end_date": today + timedelta(days=26), "assigned_staff_id": staff1.id,
            "description": "A stunning trek through the UNESCO World Heritage site, renowned for its meadows of endemic alpine flowers.",
        },
        {
            "name": "Roopkund Trek", "location": "Chamoli, Uttarakhand",
            "difficulty": "Hard", "duration_days": 8, "total_slots": 20,
            "status": "Open", "start_date": today + timedelta(days=35),
            "end_date": today + timedelta(days=43), "assigned_staff_id": staff1.id,
            "description": "Known as the Mystery Lake trek, Roopkund is famous for the skeletal remains visible at its bottom.",
        },
        {
            "name": "Hampta Pass Trek", "location": "Kullu, Himachal Pradesh",
            "difficulty": "Moderate", "duration_days": 5, "total_slots": 25,
            "status": "Open", "start_date": today + timedelta(days=15),
            "end_date": today + timedelta(days=20), "assigned_staff_id": staff2.id,
            "description": "A dramatic crossover trek from the lush Kullu valley to the barren Lahaul valley.",
        },
        {
            "name": "Kedarkantha Trek", "location": "Uttarkashi, Uttarakhand",
            "difficulty": "Easy", "duration_days": 4, "total_slots": 35,
            "status": "Open", "start_date": today + timedelta(days=10),
            "end_date": today + timedelta(days=14), "assigned_staff_id": staff2.id,
            "description": "One of the most popular winter treks in India, offering breathtaking views of the Himalayan peaks.",
        },
        {
            "name": "Kedarnath Trek", "location": "Garhwal, Uttarakhand",
            "difficulty": "Moderate", "duration_days": 6, "total_slots": 50,
            "status": "Open", "start_date": today + timedelta(days=12),
            "end_date": today + timedelta(days=18), "assigned_staff_id": staff1.id,
            "description": "A holy trail leading to the ancient Kedarnath temple, surrounded by snow-capped peaks and glaciers.",
        },
        {
            "name": "Badrinath Valley Trek", "location": "Chamoli, Uttarakhand",
            "difficulty": "Easy", "duration_days": 4, "total_slots": 45,
            "status": "Open", "start_date": today + timedelta(days=18),
            "end_date": today + timedelta(days=22), "assigned_staff_id": staff2.id,
            "description": "Explore the scenic valley around the Badrinath shrine, showcasing beautiful meadows and cascades.",
        },
        {
            "name": "Shimla Forest Sanctuary Trek", "location": "Shimla, Himachal Pradesh",
            "difficulty": "Easy", "duration_days": 3, "total_slots": 30,
            "status": "Open", "start_date": today + timedelta(days=8),
            "end_date": today + timedelta(days=11), "assigned_staff_id": staff1.id,
            "description": "A delightful trek through dense pine, oak, and cedar forests in the Himalayan foothills.",
        },
        {
            "name": "Manali Solang Valley Trek", "location": "Manali, Himachal Pradesh",
            "difficulty": "Easy", "duration_days": 3, "total_slots": 35,
            "status": "Open", "start_date": today + timedelta(days=14),
            "end_date": today + timedelta(days=17), "assigned_staff_id": staff2.id,
            "description": "A scenic trek offering spectacular views of snow-capped mountains, glaciers, and green meadows.",
        },
        {
            "name": "Pin Parvati Pass", "location": "Kullu, Himachal Pradesh",
            "difficulty": "Hard", "duration_days": 12, "total_slots": 15,
            "status": "Approved", "start_date": today + timedelta(days=60),
            "end_date": today + timedelta(days=72), "assigned_staff_id": staff1.id,
            "description": "One of the most challenging high-altitude treks connecting Spiti Valley with Kullu Valley.",
        },
        {
            "name": "Chopta Tungnath Trek", "location": "Rudraprayag, Uttarakhand",
            "difficulty": "Easy", "duration_days": 3, "total_slots": 40,
            "status": "Completed", "start_date": today - timedelta(days=30),
            "end_date": today - timedelta(days=27), "assigned_staff_id": staff2.id,
            "description": "Known as the Mini Switzerland of India, Chopta offers stunning meadows and the highest Shiva temple.",
        },
    ]

    treks = []
    for td in treks_data:
        t = Trek(
            name             = td["name"],
            description      = td["description"],
            location         = td["location"],
            difficulty       = td["difficulty"],
            duration_days    = td["duration_days"],
            total_slots      = td["total_slots"],
            available_slots  = td["total_slots"],
            status           = td["status"],
            start_date       = td["start_date"],
            end_date         = td["end_date"],
            assigned_staff_id= td["assigned_staff_id"],
        )
        db.session.add(t)
        treks.append(t)
    db.session.flush()

    # Demo Users
    users_data = [
        ("Arjun Verma",  "arjun@example.com",  "+91-9800000001"),
        ("Priya Singh",  "priya@example.com",  "+91-9800000002"),
        ("Kiran Kumar",  "kiran@example.com",  "+91-9800000003"),
        ("Divya Menon",  "divya@example.com",  "+91-9800000004"),
        ("Rohan Gupta",  "rohan@example.com",  "+91-9800000005"),
    ]
    demo_users = []
    for name, email, phone in users_data:
        u = User(name=name, email=email, phone=phone, role="user")
        u.set_password("User@123")
        db.session.add(u)
        demo_users.append(u)
    db.session.flush()

    # Demo Bookings
    open_treks = [t for t in treks if t.status == "Open"]
    completed_trek = next((t for t in treks if t.status == "Completed"), None)

    for i, user in enumerate(demo_users):
        if open_treks:
            trek = open_treks[i % len(open_treks)]
            if trek.available_slots > 0:
                b = Booking(user_id=user.id, trek_id=trek.id, status="Booked")
                trek.available_slots -= 1
                db.session.add(b)

        # Give first two users a completed booking
        if completed_trek and i < 2:
            b2 = Booking(
                user_id    = user.id,
                trek_id    = completed_trek.id,
                status     = "Completed",
                completed_at = date.today() - timedelta(days=25),
            )
            db.session.add(b2)

    db.session.commit()
    print("[PeakPath] Demo data seeded: 2 staff, 6 treks, 5 users, bookings created.")


# Entry point
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
