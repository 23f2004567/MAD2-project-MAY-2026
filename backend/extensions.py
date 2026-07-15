"""
extensions.py — Flask extension singletons.

Initialised here without an app context so they can be imported anywhere
without causing circular-import issues. The app context is bound later in
app.py via the init_app() pattern.
"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from celery import Celery

db = SQLAlchemy()
jwt = JWTManager()

# Celery instance — instantiated with default Redis configuration
celery = Celery(
    __name__,
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["tasks.celery_tasks"]
)
