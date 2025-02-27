from marshmallow import Schema, fields, validate, validates, ValidationError
from .database import db
from datetime import datetime, timezone

class UserProfileSchema(Schema):
    """
    Validation schema for user profile data.
    
    Ensures proper formatting and validation of user profile information
    before database interactions.
    """
    # Primary key (read-only)
    id = fields.Integer(dump_only=True)
    
    # Foreign key to user table
    user_id = fields.Integer(required=True)
    
    # Plant hardiness zone with format validation
    plant_hardiness_zone = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=10, error="Plant hardiness zone must be 10 characters or less.")
    )
    
    # Zip code validation
    zip_code = fields.String(
        required=False,
        allow_none=True,
        validate=[
            validate.Length(min=5, max=10, error="Zip code must be between 5 and 10 characters long."),
            validate.Regexp(r"^\d{5}(-\d{4})?$", error="Zip code must be in format 12345 or 12345-6789.")
        ]
    )
    
    # City name validation
    city = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100, error="City name must be 100 characters or less.")
    )
    
    # State name validation
    state = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50, error="State name must be 50 characters or less.")
    )
    
    # Boolean for irrigation system
    has_irrigation = fields.Boolean(required=False, allow_none=True)
    
    # Numerical fields with range validation
    sunlight_hours = fields.Float(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, max=24, error="Sunlight hours must be between 0 and 24.")
    )
    
    soil_ph = fields.Float(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, max=14, error="Soil pH must be between 0 and 14.")
    )
    
    # Timestamps (read-only)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Additional validation method for ensuring valid hardiness zone format
    @validates("plant_hardiness_zone")
    def validate_plant_hardiness_zone(self, value):
        if value is not None and not value.strip():
            raise ValidationError("Plant hardiness zone cannot be empty string.")
        
        if value is not None and not (value[0].isdigit() or value[:-1].isdigit()):
            raise ValidationError("Plant hardiness zone must start with a number (format: 5a, 7b, etc).")

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = db.relationship("User", backref="profile", uselist=False)
    