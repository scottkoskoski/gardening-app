from datetime import datetime, timezone
from marshmallow import Schema, fields, validate
from .database import db


class HarvestSchema(Schema):
    """Validation schema for harvest data."""
    id = fields.Integer(dump_only=True)
    garden_id = fields.Integer(required=True)
    plant_id = fields.Integer(required=True)
    user_id = fields.Integer(dump_only=True)
    harvest_date = fields.DateTime(
        required=False,
        load_default=None
    )
    quantity = fields.Float(
        required=True,
        validate=validate.Range(min=0, error="Quantity must be a positive number.")
    )
    unit = fields.String(
        required=True,
        validate=validate.OneOf(
            ["lbs", "kg", "oz", "count", "bunches", "bushels"],
            error="Unit must be one of: lbs, kg, oz, count, bunches, bushels."
        )
    )
    quality = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(
            ["excellent", "good", "fair", "poor"],
            error="Quality must be one of: excellent, good, fair, poor."
        )
    )
    notes = fields.String(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)

    # Read-only fields for serialization
    plant_name = fields.String(dump_only=True)
    garden_name = fields.String(dump_only=True)


class Harvest(db.Model):
    """Model representing a harvest entry for a garden plant."""
    __tablename__ = "harvest"

    id = db.Column(db.Integer, primary_key=True)
    garden_id = db.Column(db.Integer, db.ForeignKey("user_garden.id"), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    harvest_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    quality = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    garden = db.relationship("UserGarden", backref="harvests")
    plant = db.relationship("Plant", backref="harvests")
    user = db.relationship("User", backref="harvests")

    def __repr__(self):
        return f"<Harvest id={self.id} plant_id={self.plant_id} quantity={self.quantity}{self.unit}>"
