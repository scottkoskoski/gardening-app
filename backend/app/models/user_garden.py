from marshmallow import Schema, fields, validate
from datetime import datetime, timezone
from .database import db

class UserGardenSchema(Schema):
    """
    Validation schema for user garden data.
    Ensures data integrity before database interactions.
    """
    # Primary key (read-only, managed by database)
    id = fields.Integer(dump_only=True)
    
    # User association field
    user_id = fields.Integer(required=True)
    
    # Garden name with comprehensive validation
    garden_name = fields.String(
        required=True,
        validate=[
            validate.Length(min=2, max=100, error="Garden name must be 2-100 characters."),
            validate.Regexp(r'^[a-zA-Z0-9 ]+$', error="Garden name can only contain letters, numbers, and spaces.")
        ]
    )
    
    garden_type_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Garden type must be a valid ID.")
    )
    
    # Optional boolean flags for garden characteristics
    is_community_garden = fields.Boolean(required=False)
    is_rooftop_garden = fields.Boolean(required=False)
    
    # Size and dimensional fields
    garden_size = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50)
    )
    garden_dimensions = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50)
    )
    
    # Environmental and resource fields
    soil_type = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50)
    )
    water_source = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100)
    )
    
    # Garden management fields
    pest_protection = fields.Boolean(required=False)
    plant_hardiness_zone = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=10)
    )
    
    # Plant tracking fields
    preferred_plants = fields.String(required=False, allow_none=True)
    current_plants = fields.String(required=False, allow_none=True)
    
    # Timestamp fields (read-only, managed by database)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserGarden(db.Model):
    """
    SQLAlchemy model representing a user's garden.
    
    Provides a comprehensive database representation of garden properties,
    including relationships, constraints, and default behaviors.
    """
    __tablename__ = "user_garden"
    
    # Primary key and user association
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    # Garden identification and classification
    garden_name = db.Column(db.String(100))
    garden_type_id = db.Column(db.Integer, db.ForeignKey("garden_type.id"), nullable=False)
    is_community_garden = db.Column(db.Boolean)
    is_rooftop_garden = db.Column(db.Boolean)
    
    # Physical garden characteristics
    garden_size = db.Column(db.String(50))
    garden_dimensions = db.Column(db.String(50), nullable=True)
    soil_type = db.Column(db.String(50))
    water_source = db.Column(db.String(100))
    
    # Garden management attributes
    pest_protection = db.Column(db.Boolean, default=False)
    plant_hardiness_zone = db.Column(db.String(10), nullable=True)
    
    # Plant tracking
    preferred_plants = db.Column(db.Text, nullable=True)
    current_plants = db.Column(db.Text, nullable=True)
    
    # Timestamp management with timezone awareness
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship definitions
    user = db.relationship("User", backref="garden")
    garden_type = db.relationship("GardenType", backref="garden_type")