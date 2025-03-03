from marshmallow import Schema, fields, validate
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
    
class GardenTypeSchema(Schema):
    """
    Validation schema for garden type data.
    
    Ensures data integrity and provides comprehensive validation
    for garden type information before database interactions.
    """
    # Primary key (read-only, managed by database)
    id = fields.Integer(dump_only=True)
    
    # Garden type name with unique constraint validation
    name = fields.Enum(
        GardenTypeEnum,
        by_value=True,
        required=True,
        validate=validate.OneOf([t.value for t in GardenTypeEnum])
    )
    
    # Optional description with length constraint
    description = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )
    
    # Optional metadata fields with length constraints
    ideal_soil_type = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100)
    )
    
    space_requirements = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100)
    )
    
    maintenance_level = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100)
    )

class GardenType(db.Model):
    __tablename__ = "garden_type"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(GardenTypeEnum), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    ideal_soil_type = db.Column(db.String(100), nullable=True)
    space_requirements = db.Column(db.String(100), nullable=True)
    maintenance_level = db.Column(db.String(100), nullable=True)
    