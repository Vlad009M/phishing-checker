from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    checks_today = db.Column(db.Integer, default=0)
    last_reset = db.Column(db.DateTime)
    registered_at = db.Column(db.DateTime)
    account_type = db.Column(db.String(10), default='free')
    last_login = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)  # <-- ось це додай

    
    # Додаємо нове поле:
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    account_type = db.Column(db.String(20), default='free')
    checks_today = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
