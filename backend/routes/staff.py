"""
routes/staff.py — Trek Staff API endpoints.

CRITICAL SECURITY RULE: Every route that accesses a specific trek MUST verify
that trek.assigned_staff_id == current_staff.id.
This check is done in the backend — changing a URL or trek ID manually will
still be rejected.
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import User, Trek, Booking

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")

VALID_STATUSES = ("Pending", "Approved", "Open", "Closed", "Completed")


def require_staff():
    """Return (staff_user, None) or (None, error_response)."""
    from functools import wraps
    claims = get_jwt()
    if claims.get("role") != "staff":
        return None, (jsonify(success=False, message="Forbidden."), 403)
    staff = User.query.get(int(get_jwt_identity()))
    if not staff or not staff.is_active or staff.is_blacklisted:
        return None, (jsonify(success=False, message="Account is inactive or blacklisted."), 403)
    return staff, None


# Dashboard
@staff_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    staff, err = require_staff()
    if err:
        return err

    treks = Trek.query.filter_by(assigned_staff_id=staff.id).all()
    today = date.today()

    assigned_count   = len(treks)
    active_count     = sum(1 for t in treks if t.status == "Open")
    upcoming_count   = sum(1 for t in treks if t.start_date and t.start_date > today)
    total_participants = (
        Booking.query
        .filter(Booking.trek_id.in_([t.id for t in treks]), Booking.status != "Cancelled")
        .count()
    )

    trek_cards = []
    for t in treks:
        participant_count = Booking.query.filter_by(trek_id=t.id).filter(Booking.status != "Cancelled").count()
        d = t.to_dict()
        d["participant_count"] = participant_count
        trek_cards.append(d)

    return jsonify(success=True, data={
        "stats": {
            "assigned_treks":     assigned_count,
            "active_treks":       active_count,
            "upcoming_treks":     upcoming_count,
            "total_participants": total_participants,
        },
        "treks": trek_cards,
    }), 200


# List assigned treks
@staff_bp.route("/treks", methods=["GET"])
@jwt_required()
def list_treks():
    staff, err = require_staff()
    if err:
        return err

    treks = Trek.query.filter_by(assigned_staff_id=staff.id).order_by(Trek.start_date).all()
    result = []
    for t in treks:
        d = t.to_dict()
        d["participant_count"] = Booking.query.filter_by(trek_id=t.id).filter(Booking.status != "Cancelled").count()
        result.append(d)
    return jsonify(success=True, data=result), 200


# Trek detail (only assigned)
@staff_bp.route("/treks/<int:trek_id>", methods=["GET"])
@jwt_required()
def get_trek(trek_id):
    staff, err = require_staff()
    if err:
        return err

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify(success=False, message="Trek not found."), 404

    # CRITICAL: staff can only see their assigned trek
    if trek.assigned_staff_id != staff.id:
        return jsonify(success=False, message="Forbidden: not your assigned trek."), 403

    d = trek.to_dict()
    d["participant_count"] = Booking.query.filter_by(trek_id=trek.id).filter(Booking.status != "Cancelled").count()
    return jsonify(success=True, data=d), 200


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


# Update trek (only allowed fields, only assigned)
@staff_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@jwt_required()
def update_trek(trek_id):
    staff, err = require_staff()
    if err:
        return err

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify(success=False, message="Trek not found."), 404

    # CRITICAL: enforce ownership
    if trek.assigned_staff_id != staff.id:
        return jsonify(success=False, message="Forbidden: not your assigned trek."), 403

    data = request.get_json(silent=True) or {}

    # Staff can only update status and available_slots (not all trek fields)
    if "status" in data:
        new_status = data["status"]
        if new_status not in VALID_STATUSES:
            return jsonify(success=False, message=f"Invalid status."), 400
        # Enforce logical transitions: only allow reasonable moves
        allowed_transitions = {
            "Approved": ["Open"],
            "Open":     ["Closed", "Completed"],
            "Closed":   ["Completed"],
        }
        current = trek.status
        if current in allowed_transitions:
            if new_status not in allowed_transitions[current] and new_status != current:
                return jsonify(success=False, message=f"Cannot change status from {current} to {new_status}."), 400
        trek.status = new_status

    if "available_slots" in data:
        slots = int(data["available_slots"])
        if slots < 0 or slots > trek.total_slots:
            return jsonify(success=False, message="Available slots must be between 0 and total slots."), 400
        trek.available_slots = slots

    trek.updated_at = datetime.utcnow()
    invalidate_trek_cache(trek_id)
    db.session.commit()
    return jsonify(success=True, message="Trek updated.", data=trek.to_dict()), 200


# Participant list (only for assigned trek)
@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@jwt_required()
def participants(trek_id):
    staff, err = require_staff()
    if err:
        return err

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify(success=False, message="Trek not found."), 404

    # CRITICAL: ownership check
    if trek.assigned_staff_id != staff.id:
        return jsonify(success=False, message="Forbidden: not your assigned trek."), 403

    bookings = Booking.query.filter_by(trek_id=trek_id).filter(Booking.status != "Cancelled").all()
    participants_list = []
    for b in bookings:
        participants_list.append({
            "booking_id":     b.id,
            "user_id":        b.user_id,
            "user_name":      b.trekker.name if b.trekker else "—",
            "user_email":     b.trekker.email if b.trekker else "—",
            "user_phone":     b.trekker.phone if b.trekker else "—",
            "booking_status": b.status,
            "booking_date":   b.booking_date.isoformat() if b.booking_date else None,
        })
    return jsonify(success=True, data=participants_list), 200


# Mark a participant as completed
@staff_bp.route("/bookings/<int:booking_id>/complete", methods=["PUT"])
@jwt_required()
def complete_booking(booking_id):
    staff, err = require_staff()
    if err:
        return err

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify(success=False, message="Booking not found."), 404

    trek = Trek.query.get(booking.trek_id)
    # CRITICAL: ownership check via the trek
    if not trek or trek.assigned_staff_id != staff.id:
        return jsonify(success=False, message="Forbidden."), 403

    if booking.status != "Booked":
        return jsonify(success=False, message="Only active bookings can be completed."), 400

    booking.status       = "Completed"
    booking.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify(success=True, message="Participant marked as completed.", data=booking.to_dict()), 200
