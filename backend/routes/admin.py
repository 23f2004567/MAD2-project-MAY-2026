"""
routes/admin.py — All Admin-only API endpoints.

Every route is protected by @jwt_required() + require_role("admin").
The backend validates role on EVERY request — frontend guards are UX only.
"""

import json
import redis
from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import User, Trek, Booking

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# Role guard helper
def require_role(role: str):
    """Decorator that returns 403 if the JWT claims don't have the required role."""
    from functools import wraps
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != role:
                return jsonify(success=False, message="Forbidden: insufficient permissions."), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_redis():
    return redis.from_url(current_app.config["REDIS_URL"], decode_responses=True)


def invalidate_trek_cache(trek_id=None):
    """Invalidate cached trek data when content changes."""
    try:
        r = get_redis()
        r.delete("treks:open:all")
        if trek_id:
            r.delete(f"trek:{trek_id}")
        r.delete("admin:dashboard")
    except Exception:
        pass


# Dashboard
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@require_role("admin")
def dashboard():
    cache_key = "admin:dashboard"
    try:
        r = get_redis()
        cached = r.get(cache_key)
        if cached:
            return jsonify(success=True, data=json.loads(cached), cached=True), 200
    except Exception:
        pass

    total_treks    = Trek.query.count()
    total_users    = User.query.filter_by(role="user").count()
    total_staff    = User.query.filter_by(role="staff").count()
    total_bookings = Booking.query.count()

    recent_bookings = []
    for b in Booking.query.order_by(Booking.booking_date.desc()).limit(10).all():
        recent_bookings.append(b.to_dict())

    upcoming_treks = []
    today = date.today()
    for t in Trek.query.filter(Trek.start_date >= today).order_by(Trek.start_date).limit(5).all():
        upcoming_treks.append(t.to_dict())

    # Popular treks — by booking count
    from sqlalchemy import func
    popular = (
        db.session.query(Trek, func.count(Booking.id).label("booking_count"))
        .join(Booking, Booking.trek_id == Trek.id)
        .group_by(Trek.id)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
        .all()
    )
    popular_treks = [{"trek": t.to_dict(), "booking_count": c} for t, c in popular]

    # Trek status distribution
    status_counts = {}
    for row in db.session.query(Trek.status, func.count(Trek.id)).group_by(Trek.status).all():
        status_counts[row[0]] = row[1]

    data = {
        "stats": {
            "total_treks":    total_treks,
            "total_users":    total_users,
            "total_staff":    total_staff,
            "total_bookings": total_bookings,
        },
        "recent_bookings": recent_bookings,
        "upcoming_treks":  upcoming_treks,
        "popular_treks":   popular_treks,
        "status_counts":   status_counts,
    }

    try:
        r = get_redis()
        r.setex(cache_key, 120, json.dumps(data))  # 2-minute cache
    except Exception:
        pass

    return jsonify(success=True, data=data), 200


# ══════════════════════════════════════════════════════════════════════════════
# TREK MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

VALID_DIFFICULTIES = ("Easy", "Moderate", "Hard")
VALID_STATUSES     = ("Pending", "Approved", "Open", "Closed", "Completed")


@admin_bp.route("/treks", methods=["GET"])
@jwt_required()
@require_role("admin")
def list_treks():
    q      = request.args.get("q", "")
    status = request.args.get("status", "")
    query  = Trek.query
    if q:
        query = query.filter(Trek.name.ilike(f"%{q}%"))
    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)
    treks = [t.to_dict() for t in query.order_by(Trek.created_at.desc()).all()]
    return jsonify(success=True, data=treks), 200


@admin_bp.route("/treks", methods=["POST"])
@jwt_required()
@require_role("admin")
def create_trek():
    data = request.get_json(silent=True) or {}
    errors = _validate_trek_data(data)
    if errors:
        return jsonify(success=False, message=errors), 400

    start = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    end   = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    slots = int(data["total_slots"])

    trek = Trek(
        name            = data["name"].strip(),
        description     = data.get("description", "").strip(),
        location        = data["location"].strip(),
        difficulty      = data["difficulty"],
        duration_days   = int(data["duration_days"]),
        total_slots     = slots,
        available_slots = slots,
        status          = data.get("status", "Pending"),
        start_date      = start,
        end_date        = end,
        assigned_staff_id = data.get("assigned_staff_id") or None,
    )
    db.session.add(trek)
    db.session.commit()
    invalidate_trek_cache()
    return jsonify(success=True, message="Trek created.", data=trek.to_dict()), 201


@admin_bp.route("/treks/<int:trek_id>", methods=["GET"])
@jwt_required()
@require_role("admin")
def get_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return jsonify(success=True, data=trek.to_dict()), 200


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@jwt_required()
@require_role("admin")
def update_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify(success=False, message="Trek not found."), 404

    data = request.get_json(silent=True) or {}

    if "name" in data and data["name"]:
        trek.name = data["name"].strip()
    if "description" in data:
        trek.description = data["description"].strip()
    if "location" in data and data["location"]:
        trek.location = data["location"].strip()
    if "difficulty" in data and data["difficulty"] in VALID_DIFFICULTIES:
        trek.difficulty = data["difficulty"]
    if "duration_days" in data and int(data["duration_days"]) > 0:
        trek.duration_days = int(data["duration_days"])
    if "status" in data and data["status"] in VALID_STATUSES:
        trek.status = data["status"]
    if "assigned_staff_id" in data:
        trek.assigned_staff_id = data["assigned_staff_id"] or None

    # When total_slots is updated, adjust available_slots proportionally
    if "total_slots" in data and int(data["total_slots"]) > 0:
        new_total = int(data["total_slots"])
        booked = trek.total_slots - trek.available_slots
        trek.total_slots = new_total
        trek.available_slots = max(0, new_total - booked)

    if "start_date" in data and data["start_date"]:
        trek.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    if "end_date" in data and data["end_date"]:
        trek.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

    if trek.end_date < trek.start_date:
        return jsonify(success=False, message="End date must be on or after start date."), 400

    trek.updated_at = datetime.utcnow()
    db.session.commit()
    invalidate_trek_cache(trek_id)
    return jsonify(success=True, message="Trek updated.", data=trek.to_dict()), 200


@admin_bp.route("/treks/<int:trek_id>", methods=["DELETE"])
@jwt_required()
@require_role("admin")
def delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify(success=False, message="Trek not found."), 404

    # Prevent deleting treks with active bookings
    active = Booking.query.filter_by(trek_id=trek_id, status="Booked").count()
    if active > 0:
        return jsonify(success=False, message="Cannot delete trek with active bookings."), 409

    db.session.delete(trek)
    db.session.commit()
    invalidate_trek_cache(trek_id)
    return jsonify(success=True, message="Trek deleted."), 200


@admin_bp.route("/treks/<int:trek_id>/assign", methods=["PUT"])
@jwt_required()
@require_role("admin")
def assign_staff(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify(success=False, message="Trek not found."), 404

    data = request.get_json(silent=True) or {}
    staff_id = data.get("staff_id")

    if staff_id:
        staff = User.query.filter_by(id=staff_id, role="staff").first()
        if not staff:
            return jsonify(success=False, message="Staff member not found."), 404
        trek.assigned_staff_id = staff_id
    else:
        trek.assigned_staff_id = None

    trek.updated_at = datetime.utcnow()
    db.session.commit()
    invalidate_trek_cache(trek_id)
    return jsonify(success=True, message="Staff assignment updated.", data=trek.to_dict()), 200


# ══════════════════════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@require_role("admin")
def list_users():
    q     = request.args.get("q", "")
    query = User.query.filter_by(role="user")
    if q:
        query = query.filter(
            db.or_(User.name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%"))
        )
    users = [u.to_dict() for u in query.order_by(User.created_at.desc()).all()]
    return jsonify(success=True, data=users), 200


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@require_role("admin")
def get_user(user_id):
    user = User.query.get(user_id)
    if not user or user.role != "user":
        return jsonify(success=False, message="User not found."), 404
    bookings = [b.to_dict() for b in user.bookings.order_by(Booking.booking_date.desc()).all()]
    return jsonify(success=True, data=user.to_dict(), bookings=bookings), 200


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@require_role("admin")
def update_user(user_id):
    user = User.query.get(user_id)
    if not user or user.role != "user":
        return jsonify(success=False, message="User not found."), 404

    data = request.get_json(silent=True) or {}
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if "is_blacklisted" in data:
        user.is_blacklisted = bool(data["is_blacklisted"])
        # Blacklisting also deactivates the account
        if user.is_blacklisted:
            user.is_active = False

    db.session.commit()
    return jsonify(success=True, message="User updated.", data=user.to_dict()), 200


# ══════════════════════════════════════════════════════════════════════════════
# STAFF MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@admin_bp.route("/staff", methods=["GET"])
@jwt_required()
@require_role("admin")
def list_staff():
    q     = request.args.get("q", "")
    query = User.query.filter_by(role="staff")
    if q:
        query = query.filter(
            db.or_(User.name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%"))
        )
    staff_list = []
    for s in query.order_by(User.created_at.desc()).all():
        s_dict = s.to_dict()
        # Include assigned trek info
        assigned = Trek.query.filter_by(assigned_staff_id=s.id).all()
        s_dict["assigned_treks"] = [{"id": t.id, "name": t.name, "status": t.status} for t in assigned]
        staff_list.append(s_dict)
    return jsonify(success=True, data=staff_list), 200


@admin_bp.route("/staff", methods=["POST"])
@jwt_required()
@require_role("admin")
def create_staff():
    data = request.get_json(silent=True) or {}
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    phone    = (data.get("phone") or "").strip()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify(success=False, message="Name, email and password are required."), 400
    if len(password) < 6:
        return jsonify(success=False, message="Password must be at least 6 characters."), 400
    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message="Email already registered."), 409

    staff = User(name=name, email=email, phone=phone, role="staff")
    staff.set_password(password)
    db.session.add(staff)
    db.session.commit()
    invalidate_trek_cache()
    return jsonify(success=True, message="Staff account created.", data=staff.to_dict()), 201


@admin_bp.route("/staff/<int:staff_id>", methods=["PUT"])
@jwt_required()
@require_role("admin")
def update_staff(staff_id):
    staff = User.query.filter_by(id=staff_id, role="staff").first()
    if not staff:
        return jsonify(success=False, message="Staff member not found."), 404

    data = request.get_json(silent=True) or {}
    if "name" in data and data["name"]:
        staff.name = data["name"].strip()
    if "phone" in data:
        staff.phone = data["phone"].strip()
    if "is_active" in data:
        staff.is_active = bool(data["is_active"])
    if "is_blacklisted" in data:
        staff.is_blacklisted = bool(data["is_blacklisted"])
        if staff.is_blacklisted:
            staff.is_active = False
    if "password" in data and data["password"] and len(data["password"]) >= 6:
        staff.set_password(data["password"])

    db.session.commit()
    return jsonify(success=True, message="Staff updated.", data=staff.to_dict()), 200


# ══════════════════════════════════════════════════════════════════════════════
# BOOKING MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@admin_bp.route("/bookings", methods=["GET"])
@jwt_required()
@require_role("admin")
def list_bookings():
    q      = request.args.get("q", "")
    status = request.args.get("status", "")
    query  = Booking.query.join(Booking.trekker).join(Booking.trek)

    if q:
        query = query.filter(
            db.or_(User.name.ilike(f"%{q}%"), Trek.name.ilike(f"%{q}%"))
        )
    if status:
        query = query.filter(Booking.status == status)

    bookings = [b.to_dict() for b in query.order_by(Booking.booking_date.desc()).all()]
    return jsonify(success=True, data=bookings), 200


# ══════════════════════════════════════════════════════════════════════════════
# REPORTS / ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════

@admin_bp.route("/reports", methods=["GET"])
@jwt_required()
@require_role("admin")
def reports():
    from sqlalchemy import func, extract

    # Popular treks
    popular = (
        db.session.query(Trek.name, Trek.location, func.count(Booking.id).label("bookings"))
        .join(Booking, Booking.trek_id == Trek.id)
        .group_by(Trek.id)
        .order_by(func.count(Booking.id).desc())
        .limit(10)
        .all()
    )
    popular_treks = [{"name": r[0], "location": r[1], "bookings": r[2]} for r in popular]

    # Monthly booking counts (last 12 months)
    monthly = (
        db.session.query(
            func.strftime("%Y-%m", Booking.booking_date).label("month"),
            func.count(Booking.id).label("count")
        )
        .group_by(func.strftime("%Y-%m", Booking.booking_date))
        .order_by(func.strftime("%Y-%m", Booking.booking_date).desc())
        .limit(12)
        .all()
    )
    monthly_bookings = [{"month": r[0], "count": r[1]} for r in reversed(monthly)]

    # Trek status distribution
    status_dist = (
        db.session.query(Trek.status, func.count(Trek.id).label("count"))
        .group_by(Trek.status)
        .all()
    )
    trek_status = [{"status": r[0], "count": r[1]} for r in status_dist]

    # Difficulty distribution
    diff_dist = (
        db.session.query(Trek.difficulty, func.count(Trek.id).label("count"))
        .group_by(Trek.difficulty)
        .all()
    )
    difficulty_dist = [{"difficulty": r[0], "count": r[1]} for r in diff_dist]

    # User participation (users with at least one completed booking)
    active_trekkers = (
        db.session.query(func.count(func.distinct(Booking.user_id)))
        .filter(Booking.status == "Completed")
        .scalar()
    )

    return jsonify(success=True, data={
        "popular_treks":     popular_treks,
        "monthly_bookings":  monthly_bookings,
        "trek_status":       trek_status,
        "difficulty_dist":   difficulty_dist,
        "active_trekkers":   active_trekkers,
        "total_treks":       Trek.query.count(),
        "total_bookings":    Booking.query.count(),
        "completed_treks":   Trek.query.filter_by(status="Completed").count(),
    }), 200


# Internal validation helper
def _validate_trek_data(data: dict):
    required = ["name", "location", "difficulty", "duration_days", "total_slots", "start_date", "end_date"]
    for field in required:
        if not data.get(field):
            return f"Field '{field}' is required."

    if data["difficulty"] not in VALID_DIFFICULTIES:
        return f"Difficulty must be one of {VALID_DIFFICULTIES}."
    try:
        dur = int(data["duration_days"])
        if dur <= 0:
            return "Duration must be a positive number."
    except (ValueError, TypeError):
        return "Duration must be a valid number."
    try:
        slots = int(data["total_slots"])
        if slots <= 0:
            return "Total slots must be a positive number."
    except (ValueError, TypeError):
        return "Total slots must be a valid number."
    try:
        start = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end   = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        if end < start:
            return "End date must be on or after start date."
    except ValueError:
        return "Dates must be in YYYY-MM-DD format."

    return None
