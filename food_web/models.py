# models.py
from food_web import db  # ✅ Use the SINGLE db instance from __init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pytz import timezone, utc


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ContactLinks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facebook = db.Column(db.String(150))
    instagram = db.Column(db.String(150))
    whatsapp = db.Column(db.String(150))


class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255))
    start_time = db.Column(db.DateTime(timezone=True))  # ✅ Store as timezone-aware
    end_time = db.Column(db.DateTime(timezone=True))    # ✅ Store as timezone-aware
    uploaded_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(utc)
    )  # ✅ Default in UTC with timezone info
