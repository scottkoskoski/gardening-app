from .database import db

class GardenType(db.Model):
    __tablename__ = "garden_type"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    descripton = db.Column(db.Text, nullable=True)
    ideal_soil_type = db.Column(db.String(100), nullable=True)
    space_requirements = db.Column(db.String(100), nullable=True)
    maintenance_level = db.Column(db.String(100), nullable=True)
    