from datetime import datetime, timezone
from marshmallow import Schema, fields, validate
from .database import db


class JournalEntrySchema(Schema):
    """Validation schema for journal entry data."""
    id = fields.Integer(dump_only=True)
    garden_id = fields.Integer(required=True)
    user_id = fields.Integer(dump_only=True)
    entry_type = fields.String(
        required=True,
        validate=validate.OneOf(
            ["watering", "fertilizing", "pruning", "planting",
             "harvesting", "pest_control", "observation", "other"],
            error="Invalid entry type."
        )
    )
    title = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200, error="Title must be 1-200 characters.")
    )
    notes = fields.String(required=False, allow_none=True)
    entry_date = fields.DateTime(required=False)
    created_at = fields.DateTime(dump_only=True)


class JournalEntry(db.Model):
    """Model representing a garden journal entry."""
    __tablename__ = "journal_entry"

    id = db.Column(db.Integer, primary_key=True)
    garden_id = db.Column(db.Integer, db.ForeignKey("user_garden.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    entry_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    entry_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    garden = db.relationship("UserGarden", backref="journal_entries")
    user = db.relationship("User", backref="journal_entries")
