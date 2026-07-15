"""
models/trek.py — Trek model.

Represents a trekking event that can be discovered and booked by users.
Status lifecycle: Pending → Approved → Open → Closed / Completed
"""

from datetime import datetime, date
from extensions import db


class Trek(db.Model):
    __tablename__ = "treks"

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(150), nullable=False)
    description      = db.Column(db.Text, nullable=True)
    location         = db.Column(db.String(150), nullable=False)
    # Easy | Moderate | Hard
    difficulty       = db.Column(db.String(10), nullable=False, default="Easy")
    duration_days    = db.Column(db.Integer, nullable=False)
    total_slots      = db.Column(db.Integer, nullable=False)
    available_slots  = db.Column(db.Integer, nullable=False)

    # FK to users — only a staff-role user can be assigned
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Pending | Approved | Open | Closed | Completed
    status      = db.Column(db.String(20), nullable=False, default="Pending")
    start_date  = db.Column(db.Date, nullable=False)
    end_date    = db.Column(db.Date, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    bookings = db.relationship("Booking", backref="trek", lazy="dynamic")

    def to_dict(self):
        return {
            "id":               self.id,
            "name":             self.name,
            "description":      self.description,
            "location":         self.location,
            "difficulty":       self.difficulty,
            "duration_days":    self.duration_days,
            "total_slots":      self.total_slots,
            "available_slots":  self.available_slots,
            "assigned_staff_id": self.assigned_staff_id,
            "assigned_staff":   self.staff.name if self.staff else None,
            "status":           self.status,
            "start_date":       self.start_date.isoformat() if self.start_date else None,
            "end_date":         self.end_date.isoformat() if self.end_date else None,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
            "updated_at":       self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Trek {self.name} [{self.status}]>"
