from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from ..models.database import db
from ..models.journal_entry import JournalEntry, JournalEntrySchema
from ..models.user_garden import UserGarden

journal_bp = Blueprint("journal", __name__)

entry_schema = JournalEntrySchema()
entries_schema = JournalEntrySchema(many=True)


def serialize_entry(entry):
    """Serialize a JournalEntry to a dict."""
    return {
        "id": entry.id,
        "garden_id": entry.garden_id,
        "user_id": entry.user_id,
        "entry_type": entry.entry_type,
        "title": entry.title,
        "notes": entry.notes,
        "entry_date": entry.entry_date.isoformat() if entry.entry_date else None,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


@journal_bp.route("", methods=["POST"])
@jwt_required()
def create_journal_entry():
    """Create a new journal entry for a garden."""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # Validate input
    try:
        errors = entry_schema.validate(data)
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 422
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 422

    # Verify garden ownership
    garden = UserGarden.query.filter_by(id=data["garden_id"], user_id=user_id).first()
    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    try:
        entry = JournalEntry(
            garden_id=data["garden_id"],
            user_id=user_id,
            entry_type=data["entry_type"],
            title=data["title"],
            notes=data.get("notes"),
        )
        if "entry_date" in data and data["entry_date"]:
            from datetime import datetime
            if isinstance(data["entry_date"], str):
                entry.entry_date = datetime.fromisoformat(data["entry_date"].replace("Z", "+00:00"))
            else:
                entry.entry_date = data["entry_date"]

        db.session.add(entry)
        db.session.commit()

        return jsonify({
            "message": "Journal entry created successfully",
            "entry": serialize_entry(entry)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@journal_bp.route("/<int:garden_id>", methods=["GET"])
@jwt_required()
def get_journal_entries(garden_id):
    """Get all journal entries for a garden, ordered by entry_date descending."""
    user_id = get_jwt_identity()

    # Verify garden ownership
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    entries = JournalEntry.query.filter_by(
        garden_id=garden_id, user_id=user_id
    ).order_by(JournalEntry.entry_date.desc()).all()

    return jsonify({
        "entries": [serialize_entry(e) for e in entries],
        "garden_name": garden.garden_name,
    }), 200


@journal_bp.route("/<int:garden_id>/recent", methods=["GET"])
@jwt_required()
def get_recent_journal_entries(garden_id):
    """Get the 5 most recent journal entries for a garden."""
    user_id = get_jwt_identity()

    # Verify garden ownership
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    entries = JournalEntry.query.filter_by(
        garden_id=garden_id, user_id=user_id
    ).order_by(JournalEntry.entry_date.desc()).limit(5).all()

    return jsonify({
        "entries": [serialize_entry(e) for e in entries],
        "garden_name": garden.garden_name,
    }), 200


@journal_bp.route("/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def delete_journal_entry(entry_id):
    """Delete a journal entry, verifying ownership."""
    user_id = get_jwt_identity()

    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if not entry:
        return jsonify({"error": "Journal entry not found"}), 404

    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"message": "Journal entry deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete journal entry: {str(e)}"}), 500
