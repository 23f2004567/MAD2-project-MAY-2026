"""
routes/auth.py — Registration, login, logout, and /me endpoint.

Security notes:
- Passwords are hashed with Werkzeug's bcrypt wrapper.
- JWT tokens are signed with JWT_SECRET_KEY from config.
- Flask-JWT-Extended v4 requires identity to be a STRING (not a dict).
  We use the user ID (str) as identity and store role/email in
  additional_claims, accessed via get_jwt() in protected routes.
- Only 'user' role can self-register (admin/staff created by admin only).
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt, unset_jwt_cookies
)
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _make_token(user: User) -> str:
    """
    Create a JWT token.
    identity = str(user.id)  — JWT-Extended v4 requires a string identity.
    additional_claims stores role and email for use in route guards.
    """
    return create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email}
    )


# Register (users only)
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    phone    = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    confirm  = data.get("confirm_password") or ""

    # Validation
    if not name or not email or not password:
        return jsonify(success=False, message="Name, email and password are required."), 400

    if "@" not in email or "." not in email:
        return jsonify(success=False, message="Invalid email format."), 400

    if len(password) < 6:
        return jsonify(success=False, message="Password must be at least 6 characters."), 400

    if password != confirm:
        return jsonify(success=False, message="Passwords do not match."), 400

    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message="Email is already registered."), 409

    # Create user
    user = User(name=name, email=email, phone=phone, role="user")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = _make_token(user)
    return jsonify(
        success=True,
        message="Registration successful.",
        token=token,
        user=user.to_dict()
    ), 201


# Login (all roles)
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify(success=False, message="Email and password are required."), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify(success=False, message="Invalid email or password."), 401

    if not user.is_active:
        return jsonify(success=False, message="Your account has been deactivated."), 403

    if user.is_blacklisted:
        return jsonify(success=False, message="Your account has been blacklisted."), 403

    token = _make_token(user)
    return jsonify(
        success=True,
        message="Login successful.",
        token=token,
        user=user.to_dict()
    ), 200


# Logout
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # JWT is stateless; client deletes the token. We just confirm the action.
    response = jsonify(success=True, message="Logged out successfully.")
    unset_jwt_cookies(response)
    return response, 200


# Me (get current user profile)
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify(success=False, message="User not found."), 404
    return jsonify(success=True, user=user.to_dict()), 200
