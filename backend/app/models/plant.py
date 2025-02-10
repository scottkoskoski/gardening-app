from .database import db

class Plant(db.Model):
    """Represents a plant and its growing requirements."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    scientific_name = db.Column(db.String(200))
    hardiness_min = db.Column(db.String(10))
    hardiness_max = db.Column(db.String(10))
    best_temperature_min = db.Column(db.Float)
    best_temperature_max = db.Column(db.Float)
    requires_greenhouse = db.Column(db.Boolean, default=False)
    suitable_for_containers = db.Column(db.Boolean, default=False)
    growing_season = db.Column(db.String(50)) # "Spring", "Summer", "Fall", "Winter"
    water_needs = db.Column(db.String(20)) # "Low", "Medium", "High"
    sunlight = db.Column(db.String(50)) # "Full Sun", "Partial Sun", "Partial Shade", "Full Shade"
    space_required = db.Column(db.String(20)) # "Small", "Medium", "Large"
    
    def __repr__(self):
        return f"<Plant {self.name}>"