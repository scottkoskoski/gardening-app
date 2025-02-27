from marshmallow import Schema, fields, validate
from .database import db

class PlantSchema(Schema):
    """
    Validation schema for plant data.
    
    Ensures data integrity and provides comprehensive validation
    for plant information before database interactions.
    """
    # Primary key (read-only, managed by database)
    id = fields.Integer(dump_only=True)
    
    # Plant name validation
    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error="Plant name must be 1-100 characters."),
            validate.Regexp(r"^[a-zA-Z0-9 '\-]+$", error="Plant name can only contain letters, spaces, apostrophes, hyphens, and numbers.")
        ]
    )
    
    # Scientific name with optional validation
    scientific_name = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=200)
    )
    
    # Hardiness zone validation
    hardiness_min = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=10)
    )
    hardiness_max = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=10)
    )
    
    # Temperature constraints
    best_temperature_min = fields.Float(required=False, allow_none=True)
    best_temperature_max = fields.Float(required=False, allow_none=True)
    
    # Boolean flags for growing conditions
    requires_greenhouse = fields.Boolean(required=False)
    suitable_for_containers = fields.Boolean(required=False)
    
    # Categorical fields with predefined options
    growing_season = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["Spring", "Summer", "Fall", "Winter"])
    )
    
    water_needs = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["Low", "Medium", "High"])
    )
    
    sunlight = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf([
            "Full Sun",
            "Partial Sun",
            "Partial Shade",
            "Full Shade"
        ])
    )
    
    space_required = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["Small", "Medium", "Large"])
    )
    
    # OpenFarm-specific fields
    sowing_method = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50)
    )
    
    # Numerical measurements
    spread = fields.Float(required=False, allow_none=True)
    row_spacing = fields.Float(required=False, allow_none=True)
    height = fields.Float(required=False, allow_none=True)
    
    # Description and image
    description = fields.String(required=False, allow_none=True)
    image_url = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255)
    )

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
    
    # OpenFarm-specific fields
    sowing_method = db.Column(db.String(50)) # Example: "Direct sow", "Transplant"
    spread = db.Column(db.Float) # Spread in inches/cm
    row_spacing = db.Column(db.Float) # Row spacing in inches/cm
    height = db.Column(db.Float) # Height in inches/cm
    description = db.Column(db.Text) # Description of the plant
    image_url = db.Column(db.String(255)) # URL to the plant image
    
    def __repr__(self):
        return f"<Plant {self.name}>"