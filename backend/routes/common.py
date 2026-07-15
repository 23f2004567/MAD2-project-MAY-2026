"""
routes/common.py — Public trek listing (open treks, trek detail).

These endpoints are accessible without authentication.
Redis is used to cache results and reduce DB load.
"""

import json
import redis
from flask import Blueprint, request, jsonify, current_app
from models import Trek

common_bp = Blueprint("common", __name__, url_prefix="/api")


def get_redis():
    """Return a Redis client using the app's REDIS_URL config."""
    return redis.from_url(current_app.config["REDIS_URL"], decode_responses=True)


# List open treks (with search/filter + Redis cache)
@common_bp.route("/treks", methods=["GET"])
def list_treks():
    # Query params for filtering
    q          = request.args.get("q", "").strip()
    location   = request.args.get("location", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    duration   = request.args.get("duration", "").strip()

    # Only cache the unfiltered full listing (filtered results vary too much)
    cache_key = "treks:open:all"
    use_cache = not any([q, location, difficulty, duration])

    if use_cache:
        try:
            r = get_redis()
            cached = r.get(cache_key)
            if cached:
                return jsonify(success=True, data=json.loads(cached), cached=True), 200
        except Exception:
            pass  # Redis unavailable — fall through to DB query

    # DB query
    query = Trek.query.filter_by(status="Open")

    if q:
        query = query.filter(Trek.name.ilike(f"%{q}%"))
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if difficulty and difficulty in ("Easy", "Moderate", "Hard"):
        query = query.filter_by(difficulty=difficulty)
    if duration and duration.isdigit():
        query = query.filter(Trek.duration_days <= int(duration))

    treks = [t.to_dict() for t in query.order_by(Trek.start_date).all()]

    # Store in Redis for 5 minutes (300 seconds) — only for unfiltered listing
    if use_cache:
        try:
            r = get_redis()
            r.setex(cache_key, 300, json.dumps(treks))
        except Exception:
            pass

    return jsonify(success=True, data=treks, cached=False), 200


# Trek detail (with Redis cache)
@common_bp.route("/treks/<int:trek_id>", methods=["GET"])
def trek_detail(trek_id):
    cache_key = f"trek:{trek_id}"
    try:
        r = get_redis()
        cached = r.get(cache_key)
        if cached:
            return jsonify(success=True, data=json.loads(cached), cached=True), 200
    except Exception:
        pass

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify(success=False, message="Trek not found."), 404

    data = trek.to_dict()
    try:
        r = get_redis()
        r.setex(cache_key, 300, json.dumps(data))
    except Exception:
        pass

    return jsonify(success=True, data=data, cached=False), 200
