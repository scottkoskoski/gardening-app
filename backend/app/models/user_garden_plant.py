from enum import Enum
from datetime import datetime, timezone
from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow_enum import EnumField
from .database import db

class GrowthStage(Enum):
    SEEDLING = "Seedling"
    VEGETATIVE = "Vegetative"
    FLOWERING = "Flowering"
    FRUITING = "Fruiting"

class UserGardenPlantSchema(Schema):
    """
    Validation schema for user garden plant data.
    
    Ensures proper validation of plant tracking within user gardens,
    including growth stages and planting/harvest dates.
    """
    # Primary key (read-only)
    id = fields.Integer(dump_only=True)
    
    # Required foreign keys
    garden_id = fields.Integer(required=True)
    plant_id = fields.Integer(required=True)
    
    # Date fields with validation
    planted_at = fields.DateTime(
        default=lambda: datetime.now(timezone.utc)
    )
    
    expected_harvest_date = fields.DateTime(
        required=False,
        allow_none=True
    )
    
    # Growth stage using EnumField for validation
    growth_stage = EnumField(
        GrowthStage,
        by_value=True,
        default=GrowthStage.SEEDLING
    )
    
    @validates("expected_harvest_date")
    def validate_harvest_date(self, value):
        """Validates that expected harvest date is in the future."""
        if value and value < datetime.now(timezone.utc):
            raise ValidationError("Expected harvest date must be in the future.")
    
    class Meta:
        """Meta options for UserGardenPlantSchema."""
        fields = ("id", "garden_id", "plant_id", "planted_at", "expected_harvest_date", "growth_stage")

class UserGardenPlant(db.Model):
    __tablename__ = "user_garden_plant"
    
    id = db.Column(db.Integer, primary_key=True)
    garden_id = db.Column(db.Integer, db.ForeignKey("user_garden.id"), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"), nullable=False)
    planted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expected_harvest_date = db.Column(db.DateTime, nullable=True)
    growth_stage = db.Column(db.Enum(GrowthStage), nullable=False, default=GrowthStage.SEEDLING)
    
    garden = db.relationship("UserGarden", backref="garden_plants", lazy="joined")
    plant = db.relationship("Plant", backref="plant_gardens")
    