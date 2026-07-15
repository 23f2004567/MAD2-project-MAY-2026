"""
models/__init__.py — imports all models so SQLAlchemy can discover them
when db.create_all() is called in app.py.
"""

from .user import User
from .trek import Trek
from .booking import Booking
