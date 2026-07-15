"""
models/booking.py — Booking model.

Links a user to a trek. Business rules (slot limits, duplicate prevention,
status checks) are enforced in the route layer, NOT here in the model.
"""

from datetime import datetime
from extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id        = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date   = db.Column(db.DateTime, default=datetime.utcnow)
    # Booked | Cancelled | Completed
    status         = db.Column(db.String(20), nullable=False, default="Booked")
    # Pending | Paid  (optional payment tracking)
    payment_status = db.Column(db.String(20), nullable=False, default="Pending")
    completed_at   = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id":             self.id,
            "user_id":        self.user_id,
            "user_name":      self.trekker.name if self.trekker else None,
            "user_email":     self.trekker.email if self.trekker else None,
            "trek_id":        self.trek_id,
            "trek_name":      self.trek.name if self.trek else None,
            "trek_location":  self.trek.location if self.trek else None,
            "trek_start":     self.trek.start_date.isoformat() if self.trek and self.trek.start_date else None,
            "trek_end":       self.trek.end_date.isoformat() if self.trek and self.trek.end_date else None,
            "booking_date":   self.booking_date.isoformat() if self.booking_date else None,
            "status":         self.status,
            "payment_status": self.payment_status,
            "completed_at":   self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self):
        return f"<Booking user={self.user_id} trek={self.trek_id} [{self.status}]>"
