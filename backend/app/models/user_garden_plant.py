from .database import db
from datetime import datetime, timezone

class UserGardenPlant(db.Model):
    __tablename__ = "user_garden_plant"
    
    id = db.Column(db.Integer, primary_key=True)
    garden_id = db.Column(db.Integer, db.ForeignKey("user_garden.id"), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"), nullable=False)
    planted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expected_harvest_date = db.Column(db.DateTime, nullable=True)
    growth_stage = db.Column(db.String(50), nullable=True)
    
    garden = db.relationship("UserGarden", backref="garden_plants", lazy="joined")
    plant = db.relationship("Plant", backref="plant_gardens")
    