from datetime import datetime, timezone
from .database import db

class UserGarden(db.Model):
    __tablename__ = "user_garden"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    garden_name = db.Column(db.String(100))
    garden_type_id = db.Column(db.Integer, db.ForeignKey("garden_type.id"), nullable=False)
    is_community_garden = db.Column(db.Boolean)
    is_rooftop_garden = db.Column(db.Boolean)
    garden_size = db.Column(db.String(50))
    garden_dimensions = db.Column(db.String(50), nullable=True)
    soil_type = db.Column(db.String(50))
    water_source = db.Column(db.String(100))
    pest_protection = db.Column(db.Boolean, default=False)
    plant_hardiness_zone = db.Column(db.String(10), nullable=True)
    preferred_plants = db.Column(db.Text, nullable=True)
    current_plants = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = db.relationship("User", backref="garden")
    garden_type = db.relationship("GardenType", backref="garden_type")