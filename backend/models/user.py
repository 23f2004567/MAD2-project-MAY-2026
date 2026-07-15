"""
models/user.py — User model.

Represents all three roles: admin, staff, and user (trekker).
A single unified model is used; the `role` field differentiates behaviour.
"""

from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    password_hash  = db.Column(db.String(255), nullable=False)
    phone          = db.Column(db.String(20), nullable=True)
    # Role must be one of: admin | staff | user
    role           = db.Column(db.String(10), nullable=False, default="user")
    is_active      = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # A staff member can be assigned to many treks (via Trek.assigned_staff_id)
    assigned_treks = db.relationship(
        "Trek",
        foreign_keys="Trek.assigned_staff_id",
        backref="staff",
        lazy="dynamic",
    )
    bookings = db.relationship("Booking", backref="trekker", lazy="dynamic")

    # Password helpers
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # Serialisation helper
    def to_dict(self, include_sensitive=False):
        data = {
            "id":             self.id,
            "name":           self.name,
            "email":          self.email,
            "phone":          self.phone,
            "role":           self.role,
            "is_active":      self.is_active,
            "is_blacklisted": self.is_blacklisted,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
        }
        return data

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"
