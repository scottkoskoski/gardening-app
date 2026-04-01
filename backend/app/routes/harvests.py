from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import func, extract
from datetime import datetime, timezone
from ..models.database import db
from ..models.harvest import Harvest, HarvestSchema
from ..models.user_garden import UserGarden
from ..models.plant import Plant

harvests_bp = Blueprint("harvests", __name__)

harvest_schema = HarvestSchema()
harvests_schema = HarvestSchema(many=True)


@harvests_bp.route("", methods=["POST"])
@jwt_required()
def log_harvest():
    """Log a new harvest entry."""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # Validate ownership of garden
    garden = UserGarden.query.filter_by(id=data.get("garden_id"), user_id=user_id).first()
    if not garden:
        return jsonify({"error": "Garden not found or access denied"}), 404

    # Validate plant exists
    plant = Plant.query.get(data.get("plant_id"))
    if not plant:
        return jsonify({"error": "Plant not found"}), 404

    try:
        errors = harvest_schema.validate(data)
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 422

        harvest = Harvest(
            garden_id=data["garden_id"],
            plant_id=data["plant_id"],
            user_id=user_id,
            quantity=data["quantity"],
            unit=data["unit"],
            quality=data.get("quality"),
            notes=data.get("notes"),
            harvest_date=datetime.fromisoformat(data["harvest_date"]) if data.get("harvest_date") else datetime.now(timezone.utc),
        )

        db.session.add(harvest)
        db.session.commit()

        return jsonify({
            "message": "Harvest logged successfully",
            "harvest_id": harvest.id
        }), 201

    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@harvests_bp.route("/<int:garden_id>", methods=["GET"])
@jwt_required()
def get_harvests(garden_id):
    """Get all harvests for a garden, ordered by harvest_date desc."""
    user_id = get_jwt_identity()

    # Verify garden ownership
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()
    if not garden:
        return jsonify({"error": "Garden not found or access denied"}), 404

    harvests = Harvest.query.filter_by(garden_id=garden_id, user_id=user_id)\
        .order_by(Harvest.harvest_date.desc()).all()

    result = []
    for h in harvests:
        result.append({
            "id": h.id,
            "garden_id": h.garden_id,
            "plant_id": h.plant_id,
            "plant_name": h.plant.name if h.plant else "Unknown",
            "harvest_date": h.harvest_date.isoformat() if h.harvest_date else None,
            "quantity": h.quantity,
            "unit": h.unit,
            "quality": h.quality,
            "notes": h.notes,
            "created_at": h.created_at.isoformat() if h.created_at else None,
        })

    return jsonify({
        "harvests": result,
        "garden_name": garden.garden_name,
    }), 200


@harvests_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_harvest_summary():
    """Get harvest summary across all user's gardens."""
    user_id = get_jwt_identity()

    # Total harvests count
    total_count = Harvest.query.filter_by(user_id=user_id).count()

    # Total quantity by plant
    quantity_by_plant = db.session.query(
        Plant.name,
        func.sum(Harvest.quantity).label("total_quantity"),
        Harvest.unit
    ).join(Plant, Harvest.plant_id == Plant.id)\
     .filter(Harvest.user_id == user_id)\
     .group_by(Plant.name, Harvest.unit)\
     .order_by(func.sum(Harvest.quantity).desc())\
     .all()

    plants_summary = []
    for name, total_qty, unit in quantity_by_plant:
        plants_summary.append({
            "plant_name": name,
            "total_quantity": round(total_qty, 2),
            "unit": unit,
        })

    # Harvests by month (last 12 months)
    harvests_by_month = db.session.query(
        extract("year", Harvest.harvest_date).label("year"),
        extract("month", Harvest.harvest_date).label("month"),
        func.count(Harvest.id).label("count"),
        func.sum(Harvest.quantity).label("total_quantity"),
    ).filter(Harvest.user_id == user_id)\
     .group_by("year", "month")\
     .order_by("year", "month")\
     .all()

    monthly_data = []
    for year, month, count, total_qty in harvests_by_month:
        monthly_data.append({
            "year": int(year),
            "month": int(month),
            "count": count,
            "total_quantity": round(total_qty, 2),
        })

    # Best performing plants (top 5 by total quantity)
    best_plants = plants_summary[:5]

    # Get user's gardens for linking
    gardens = UserGarden.query.filter_by(user_id=user_id).all()
    gardens_list = [{"id": g.id, "garden_name": g.garden_name} for g in gardens]

    return jsonify({
        "total_harvests": total_count,
        "plants_summary": plants_summary,
        "monthly_data": monthly_data,
        "best_plants": best_plants,
        "gardens": gardens_list,
    }), 200


@harvests_bp.route("/<int:harvest_id>", methods=["DELETE"])
@jwt_required()
def delete_harvest(harvest_id):
    """Delete a harvest entry (verify ownership)."""
    user_id = get_jwt_identity()

    harvest = Harvest.query.filter_by(id=harvest_id, user_id=user_id).first()
    if not harvest:
        return jsonify({"error": "Harvest not found or access denied"}), 404

    try:
        db.session.delete(harvest)
        db.session.commit()
        return jsonify({"message": "Harvest deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete harvest: {str(e)}"}), 500
