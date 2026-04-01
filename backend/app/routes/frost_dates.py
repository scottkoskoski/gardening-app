import requests
from datetime import date
from flask import Blueprint, request, jsonify

frost_dates_bp = Blueprint("frost_dates", __name__)

# USDA API URL for hardiness zone lookup
USDA_API_URL = "https://phzmapi.org/"

# Typical frost date ranges per USDA hardiness zone (month, day)
FROST_DATA = {
    3:  {"last_frost": (5, 15), "first_frost": (9, 15)},
    4:  {"last_frost": (5, 10), "first_frost": (9, 25)},
    5:  {"last_frost": (4, 30), "first_frost": (10, 5)},
    6:  {"last_frost": (4, 15), "first_frost": (10, 15)},
    7:  {"last_frost": (4, 1),  "first_frost": (10, 30)},
    8:  {"last_frost": (3, 15), "first_frost": (11, 15)},
    9:  {"last_frost": (2, 15), "first_frost": (12, 1)},
    10: {"last_frost": (1, 31), "first_frost": (12, 15)},
}


def parse_zone_number(zone_str):
    """Extract the numeric zone from a zone string like '7a' or '10b'."""
    digits = ""
    for ch in zone_str:
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    return int(digits) if digits else None


def get_frost_dates_for_zone(zone_str):
    """Return frost date info for a given zone string."""
    zone_num = parse_zone_number(zone_str)
    if zone_num is None:
        return None

    current_year = 2026

    # Zone 11+ is year-round growing
    if zone_num >= 11:
        return {
            "zone": zone_str,
            "last_frost": None,
            "first_frost": None,
            "growing_season_days": 365,
            "year_round": True,
        }

    # Clamp to our data range
    lookup_zone = max(3, min(10, zone_num))
    data = FROST_DATA[lookup_zone]

    last_frost_date = date(current_year, data["last_frost"][0], data["last_frost"][1])
    first_frost_date = date(current_year, data["first_frost"][0], data["first_frost"][1])
    growing_days = (first_frost_date - last_frost_date).days

    return {
        "zone": zone_str,
        "last_frost": last_frost_date.isoformat(),
        "first_frost": first_frost_date.isoformat(),
        "growing_season_days": growing_days,
        "year_round": False,
    }


@frost_dates_bp.route("", methods=["GET"])
def frost_dates():
    """Returns estimated first and last frost dates for a location.

    Accepts either a `zip` query param (looks up zone via USDA API)
    or a `zone` query param directly (e.g. '7a').
    """
    zip_code = request.args.get("zip")
    zone = request.args.get("zone")

    if not zip_code and not zone:
        return jsonify({"error": "Either 'zip' or 'zone' parameter is required."}), 400

    # If zip provided, look up the zone
    if zip_code and not zone:
        try:
            response = requests.get(f"{USDA_API_URL}/{zip_code}.json")
            if response.status_code != 200:
                return jsonify({"error": "Failed to fetch hardiness zone for ZIP code."}), 500
            data = response.json()
            zone = data.get("zone")
            if not zone:
                return jsonify({"error": "Could not determine hardiness zone for this ZIP code."}), 404
        except Exception:
            return jsonify({"error": "Failed to look up hardiness zone."}), 500

    result = get_frost_dates_for_zone(zone)
    if result is None:
        return jsonify({"error": f"Invalid zone: {zone}"}), 400

    return jsonify(result), 200
