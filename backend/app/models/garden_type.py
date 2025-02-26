from enum import Enum
from .database import db

class GardenTypeEnum(Enum):
    RAISED_BED = "Raised Bed"
    CONTAINER = "Container Garden"
    TRADITIONAL_ROW = "Traditional Row"
    GREENHOUSE = "Greenhouse Garden"
    VERTICAL = "Vertical Garden"
    HYDROPONIC = "Hydroponic Garden"
    PERMACULTURE = "Permaculture Garden"
    COMMUNITY = "Community Garden"
    WILDLIFE_GARDEN = "Wildlife Garden"
    ROOFTOP = "Rooftop Garden"

class GardenType(db.Model):
    __tablename__ = "garden_type"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(GardenTypeEnum), unique=True, nullable=False)
    descripton = db.Column(db.Text, nullable=True)
    ideal_soil_type = db.Column(db.String(100), nullable=True)
    space_requirements = db.Column(db.String(100), nullable=True)
    maintenance_level = db.Column(db.String(100), nullable=True)
    