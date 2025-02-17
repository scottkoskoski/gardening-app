from .database import db
from datetime import datetime

class UserProfile(db.Model):
    __tablename__ = "user_profile"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    plant_hardiness_zone = db.Column(db.String(10), nullable=True)
    zip_code = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    has_irrigation = db.Column(db.Boolean, nullable=True)
    sunlight_hours = db.Column(db.Float, nullable=True)
    soil_ph = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship("User", backref="profile", uselist=False)
    