from .database import db
from datetime import datetime

class UserGarden(db.Model):
    __tablename__ = "user_garden"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    garden_name = db.Column(db.String(100))
    garden_type_id = db.Column(db.Integer, db.ForeignKey("garden_type.id"))
    is_community_garden = db.Column(db.Boolean)
    is_rooftop_garden = db.Column(db.Boolean)
    garden_size = db.Column(db.String(50))
    soil_type = db.Column(db.String(50))
    water_source = db.Column(db.String(100))
    pest_protection = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship("User", backref="garden")
    garden_type = db.relationship("GardenType", backref="garden_type")