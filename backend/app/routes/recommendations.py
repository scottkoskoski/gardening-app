from datetime import date
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.database import db
from ..models.plant import Plant
from ..models.profile import UserProfile
from .frost_dates import parse_zone_number

recommendations_bp = Blueprint("recommendations", __name__)

# Map months to seasons
MONTH_TO_SEASON = {
    1: "Winter", 2: "Winter", 3: "Spring",
    4: "Spring", 5: "Spring", 6: "Summer",
    7: "Summer", 8: "Summer", 9: "Fall",
    10: "Fall", 11: "Fall", 12: "Winter",
}

# Sunlight hours to category mapping
def sunlight_category(hours):
    if hours is None:
        return None
    if hours < 3:
        return "Full Shade"
    elif hours < 5:
        return "Partial Shade"
    elif hours < 7:
        return "Partial Sun"
    else:
        return "Full Sun"


def zone_in_range(user_zone_str, plant_min_str, plant_max_str):
    """Check if user's zone falls within a plant's hardiness range."""
    if not user_zone_str:
        return None
    user_num = parse_zone_number(user_zone_str)
    if user_num is None:
        return None

    if not plant_min_str and not plant_max_str:
        return None  # No data available

    min_num = parse_zone_number(plant_min_str) if plant_min_str else None
    max_num = parse_zone_number(plant_max_str) if plant_max_str else None

    if min_num is not None and max_num is not None:
        return min_num <= user_num <= max_num
    elif min_num is not None:
        return user_num >= min_num
    elif max_num is not None:
        return user_num <= max_num
    return None


def score_plant(plant, user_zone, user_sunlight_hours, user_has_irrigation, current_season):
    """Score a plant based on user conditions. Returns (score, max_score, reasons, warnings)."""
    score = 0
    max_score = 100
    reasons = []
    warnings = []

    # Zone compatibility (30 pts)
    zone_result = zone_in_range(user_zone, plant.hardiness_min, plant.hardiness_max)
    if zone_result is True:
        score += 30
        zone_num = parse_zone_number(user_zone) if user_zone else None
        reasons.append(f"Great for your zone {zone_num or user_zone}")
    elif zone_result is False:
        warnings.append(f"May not thrive in your zone {user_zone}")
    else:
        # No zone data for plant, give partial credit
        score += 15

    # Season timing (25 pts)
    if plant.growing_season:
        if plant.growing_season == current_season:
            score += 25
            reasons.append(f"Perfect for {current_season.lower()} planting")
        else:
            # Adjacent seasons get partial credit
            season_order = ["Spring", "Summer", "Fall", "Winter"]
            try:
                current_idx = season_order.index(current_season)
                plant_idx = season_order.index(plant.growing_season)
                distance = min(abs(current_idx - plant_idx), 4 - abs(current_idx - plant_idx))
                if distance == 1:
                    score += 12
                    reasons.append(f"Can be started soon ({plant.growing_season} plant)")
                else:
                    warnings.append(f"Best planted in {plant.growing_season}")
            except ValueError:
                score += 12
    else:
        score += 12  # No season data, partial credit

    # Sunlight match (20 pts)
    user_sun = sunlight_category(user_sunlight_hours)
    if user_sun and plant.sunlight:
        if user_sun == plant.sunlight:
            score += 20
            reasons.append("Matches your sunlight conditions")
        else:
            # Partial match for adjacent categories
            sun_order = ["Full Shade", "Partial Shade", "Partial Sun", "Full Sun"]
            try:
                user_idx = sun_order.index(user_sun)
                plant_idx = sun_order.index(plant.sunlight)
                diff = abs(user_idx - plant_idx)
                if diff == 1:
                    score += 12
                    warnings.append(f"Prefers {plant.sunlight} (you have {user_sun})")
                else:
                    score += 4
                    warnings.append(f"Needs {plant.sunlight} but you have {user_sun}")
            except ValueError:
                score += 10
    else:
        score += 10  # No data, partial credit

    # Water match (15 pts)
    if plant.water_needs:
        if user_has_irrigation:
            score += 15
            if plant.water_needs == "Low":
                reasons.append("Low water needs - easy to maintain")
            elif plant.water_needs == "High":
                reasons.append("Your irrigation system supports its high water needs")
        else:
            if plant.water_needs in ("Low", "Medium"):
                score += 15
                reasons.append("Manageable water needs without irrigation")
            else:
                score += 5
                warnings.append("High water needs - consider irrigation")
    else:
        score += 8  # No data, partial credit

    # Space efficiency (10 pts)
    if plant.space_required:
        if plant.space_required == "Small":
            score += 10
            reasons.append("Space efficient - great for small areas")
        elif plant.space_required == "Medium":
            score += 7
        elif plant.space_required == "Large":
            score += 4
            warnings.append("Requires significant growing space")
    else:
        score += 5  # No data, partial credit

    return score, max_score, reasons, warnings


def plant_to_dict(plant, score, max_score, reasons, warnings):
    return {
        "plant_id": plant.id,
        "name": plant.name,
        "scientific_name": plant.scientific_name,
        "image_url": plant.image_url,
        "description": plant.description,
        "score": score,
        "max_score": max_score,
        "reasons": reasons,
        "warnings": warnings,
        "growing_season": plant.growing_season,
        "sunlight": plant.sunlight,
        "water_needs": plant.water_needs,
        "space_required": plant.space_required,
    }


@recommendations_bp.route("", methods=["GET"])
@jwt_required()
def get_recommendations():
    """Return personalized plant recommendations based on user profile."""
    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not profile or not profile.plant_hardiness_zone:
        return jsonify({
            "error": "Profile incomplete. Please set your ZIP code and hardiness zone.",
            "profile_incomplete": True,
        }), 400

    user_zone = profile.plant_hardiness_zone
    user_sunlight_hours = profile.sunlight_hours
    user_has_irrigation = profile.has_irrigation or False

    today = date.today()
    current_season = MONTH_TO_SEASON[today.month]

    plants = Plant.query.all()
    scored = []
    for plant in plants:
        s, ms, reasons, warnings = score_plant(
            plant, user_zone, user_sunlight_hours, user_has_irrigation, current_season
        )
        scored.append(plant_to_dict(plant, s, ms, reasons, warnings))

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_20 = scored[:20]

    return jsonify({
        "recommendations": top_20,
        "zone": user_zone,
        "season": current_season,
    }), 200


@recommendations_bp.route("/seasonal", methods=["GET"])
@jwt_required()
def get_seasonal_recommendations():
    """Return plants to plant right now based on current season and zone."""
    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first()

    if not profile or not profile.plant_hardiness_zone:
        return jsonify({
            "error": "Profile incomplete. Please set your ZIP code and hardiness zone.",
            "profile_incomplete": True,
        }), 400

    user_zone = profile.plant_hardiness_zone
    user_sunlight_hours = profile.sunlight_hours
    user_has_irrigation = profile.has_irrigation or False

    today = date.today()
    current_season = MONTH_TO_SEASON[today.month]

    # Get the next season for indoor starts
    season_order = ["Spring", "Summer", "Fall", "Winter"]
    current_idx = season_order.index(current_season)
    next_season = season_order[(current_idx + 1) % 4]

    plants = Plant.query.all()
    seasonal_results = []

    for plant in plants:
        activity = None

        # Direct sow: matches current season
        if plant.growing_season == current_season:
            if plant.sowing_method and "transplant" in plant.sowing_method.lower():
                activity = "Transplant soon"
            elif plant.sowing_method and "direct" in plant.sowing_method.lower():
                activity = "Direct sow now"
            else:
                activity = "Plant now"
        # Start indoors: next season's plants
        elif plant.growing_season == next_season:
            if plant.requires_greenhouse or (
                plant.sowing_method and "transplant" in (plant.sowing_method or "").lower()
            ):
                activity = "Start indoors"
            else:
                continue
        else:
            continue

        s, ms, reasons, warnings = score_plant(
            plant, user_zone, user_sunlight_hours, user_has_irrigation, current_season
        )
        result = plant_to_dict(plant, s, ms, reasons, warnings)
        result["activity"] = activity
        seasonal_results.append(result)

    seasonal_results.sort(key=lambda x: x["score"], reverse=True)

    return jsonify({
        "seasonal": seasonal_results[:20],
        "zone": user_zone,
        "season": current_season,
        "month": today.strftime("%B"),
    }), 200
