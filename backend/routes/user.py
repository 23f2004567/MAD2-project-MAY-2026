"""
routes/user.py — Authenticated User/Trekker endpoints.

Booking business rules enforced here (backend is authoritative):
1. Trek must be Open.
2. No duplicate active bookings for the same trek.
3. available_slots must not go negative.
4. Inactive/blacklisted users cannot book.
5. Cancellation restores one available slot.
6. CSV export is queued as a Celery task (async).
"""

import os
from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import User, Trek, Booking

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


def get_current_user():
    """Return (user, None) or (None, error_response)."""
    claims = get_jwt()
    if claims.get("role") != "user":
        return None, (jsonify(success=False, message="Forbidden."), 403)
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return None, (jsonify(success=False, message="User not found."), 404)
    return user, None


def invalidate_trek_cache(trek_id=None):
    """Invalidate cached treks when slot counts change."""
    import json, redis
    try:
        r = redis.from_url(current_app.config["REDIS_URL"], decode_responses=True)
        r.delete("treks:open:all")
        if trek_id:
            r.delete(f"trek:{trek_id}")
    except Exception:
        pass


# Dashboard
@user_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user, err = get_current_user()
    if err:
        return err

    today = date.today()
    bookings = user.bookings.all()

    upcoming = [
        b.to_dict() for b in bookings
        if b.status == "Booked" and b.trek and b.trek.start_date and b.trek.start_date >= today
    ]
    completed = [b.to_dict() for b in bookings if b.status == "Completed"]

    # Recommended open treks the user hasn't booked yet
    booked_trek_ids = {b.trek_id for b in bookings if b.status in ("Booked",)}
    open_treks = (
        Trek.query.filter_by(status="Open")
        .filter(Trek.id.notin_(booked_trek_ids))
        .order_by(Trek.start_date)
        .limit(6)
        .all()
    )

    return jsonify(success=True, data={
        "user": user.to_dict(),
        "stats": {
            "available_treks":  Trek.query.filter_by(status="Open").count(),
            "upcoming_bookings": len(upcoming),
            "completed_treks":  len(completed),
            "total_bookings":   len(bookings),
        },
        "upcoming_bookings": upcoming[:3],
        "recommended_treks": [t.to_dict() for t in open_treks],
    }), 200


# Profile
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user, err = get_current_user()
    if err:
        return err
    return jsonify(success=True, data=user.to_dict()), 200


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user, err = get_current_user()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    if "name" in data and data["name"]:
        user.name = data["name"].strip()
    if "phone" in data:
        user.phone = data["phone"].strip()
    if "password" in data and data["password"]:
        if len(data["password"]) < 6:
            return jsonify(success=False, message="Password must be at least 6 characters."), 400
        if data.get("confirm_password") != data["password"]:
            return jsonify(success=False, message="Passwords do not match."), 400
        user.set_password(data["password"])

    db.session.commit()
    return jsonify(success=True, message="Profile updated.", data=user.to_dict()), 200


# My Bookings
@user_bp.route("/bookings", methods=["GET"])
@jwt_required()
def list_bookings():
    user, err = get_current_user()
    if err:
        return err
    bookings = [b.to_dict() for b in user.bookings.order_by(Booking.booking_date.desc()).all()]
    return jsonify(success=True, data=bookings), 200


# Create Booking
@user_bp.route("/bookings", methods=["POST"])
@jwt_required()
def create_booking():
    user, err = get_current_user()
    if err:
        return err

    # Rule 4: Inactive/blacklisted cannot book
    if not user.is_active:
        return jsonify(success=False, message="Your account is inactive. Contact support."), 403
    if user.is_blacklisted:
        return jsonify(success=False, message="Your account has been blacklisted."), 403

    data    = request.get_json(silent=True) or {}
    trek_id = data.get("trek_id")
    if not trek_id:
        return jsonify(success=False, message="trek_id is required."), 400

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify(success=False, message="Trek not found."), 404

    # Rule 1: Trek must be Open
    if trek.status != "Open":
        return jsonify(success=False, message="This trek is not open for booking."), 409

    # Rule 2: No duplicate active booking
    existing = Booking.query.filter_by(
        user_id=user.id, trek_id=trek_id, status="Booked"
    ).first()
    if existing:
        return jsonify(success=False, message="You already have an active booking for this trek."), 409

    # Rule 3: Check slot availability (available_slots must not go negative)
    if trek.available_slots <= 0:
        return jsonify(success=False, message="This trek is fully booked."), 409

    # Rule 7: Reduce available slots atomically
    trek.available_slots -= 1
    booking = Booking(user_id=user.id, trek_id=trek_id)
    db.session.add(booking)
    db.session.commit()
    invalidate_trek_cache(trek_id)

    return jsonify(success=True, message="Trek booked successfully.", data=booking.to_dict()), 201


# Cancel Booking
@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_booking(booking_id):
    user, err = get_current_user()
    if err:
        return err

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify(success=False, message="Booking not found."), 404

    # Users can only cancel their own bookings
    if booking.user_id != user.id:
        return jsonify(success=False, message="Forbidden."), 403

    if booking.status != "Booked":
        return jsonify(success=False, message="Only active bookings can be cancelled."), 409

    # Rule 8: Restore one slot on valid cancellation
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots = min(trek.total_slots, trek.available_slots + 1)

    booking.status = "Cancelled"
    db.session.commit()
    invalidate_trek_cache(booking.trek_id)

    return jsonify(success=True, message="Booking cancelled.", data=booking.to_dict()), 200


# Trekking History
@user_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user, err = get_current_user()
    if err:
        return err
    past = [
        b.to_dict() for b in user.bookings.filter(
            Booking.status.in_(["Completed", "Cancelled"])
        ).order_by(Booking.booking_date.desc()).all()
    ]
    return jsonify(success=True, data=past), 200


# Async CSV Export (queues a Celery task)
@user_bp.route("/export-history", methods=["POST"])
@jwt_required()
def export_history():
    user, err = get_current_user()
    if err:
        return err

    from tasks.celery_tasks import export_user_booking_history

    try:
        # Try async first (requires Celery worker + Redis broker)
        task = export_user_booking_history.delay(user.id)
        return jsonify(
            success=True,
            message="Export started. Use the task_id to check progress.",
            task_id=task.id,
            mode="async"
        ), 202
    except Exception as broker_err:
        # Celery broker unavailable — run synchronously and return a fake task_id
        current_app.logger.warning(f"Celery broker unavailable, running export synchronously: {broker_err}")
        try:
            result = export_user_booking_history.apply(args=[user.id])
            filename = result.get()
            # Return a synthetic task_id that resolves immediately via a special prefix
            return jsonify(
                success=True,
                message="Export completed synchronously (Celery not running).",
                task_id=f"sync::{filename}",
                mode="sync"
            ), 200
        except Exception as sync_err:
            return jsonify(success=False, message=f"Export failed: {sync_err}"), 500


# Check Export Task Status
@user_bp.route("/export-status/<task_id>", methods=["GET"])
@jwt_required()
def export_status(task_id):
    # Handle synchronous fallback task IDs (format: "sync::filename")
    if task_id.startswith("sync::"):
        filename = task_id[6:]
        return jsonify(success=True, state="SUCCESS",
                       message="Export ready (sync).", filename=filename), 200

    from celery.result import AsyncResult
    from extensions import celery as celery_app

    result = AsyncResult(task_id, app=celery_app)
    if result.state == "PENDING":
        return jsonify(success=True, state="PENDING", message="Export is queued."), 200
    elif result.state == "SUCCESS":
        return jsonify(success=True, state="SUCCESS", message="Export ready.", filename=result.result), 200
    elif result.state == "FAILURE":
        return jsonify(success=False, state="FAILURE", message="Export failed."), 500
    else:
        return jsonify(success=True, state=result.state, message="Export in progress."), 200


# Download CSV
@user_bp.route("/export-download/<filename>", methods=["GET"])
@jwt_required()
def export_download(filename):
    # Sanitize filename to prevent path traversal attacks
    safe_name = os.path.basename(filename)
    export_dir = current_app.config["EXPORT_DIR"]
    filepath = os.path.join(export_dir, safe_name)

    if not os.path.exists(filepath):
        return jsonify(success=False, message="File not found or expired."), 404

    return send_from_directory(export_dir, safe_name, as_attachment=True)
