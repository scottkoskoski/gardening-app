from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from ..models.plant import Plant
from .frost_dates import FROST_DATA, parse_zone_number

planting_calendar_bp = Blueprint("planting_calendar", __name__)

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

CURRENT_YEAR = 2026


def _month_from_date(d):
    """Return the month number (1-12) for a date."""
    return d.month


def _weeks_before(base_date, weeks):
    """Return a date that is `weeks` weeks before `base_date`."""
    return base_date - timedelta(weeks=weeks)


def _weeks_after(base_date, weeks):
    """Return a date that is `weeks` weeks after `base_date`."""
    return base_date + timedelta(weeks=weeks)


def _clamp_month(month):
    """Clamp month to 1-12 range."""
    return max(1, min(12, month))


def _generate_activities_for_plant(plant, last_frost_date, first_frost_date, year_round):
    """Generate month-keyed activities for a single plant based on its growing season."""
    activities = {}  # month -> list of (activity, category)

    def add(month, activity, category):
        m = _clamp_month(month)
        activities.setdefault(m, []).append({"activity": activity, "category": category})

    season = (plant.growing_season or "").strip()

    if year_round or not last_frost_date or not first_frost_date:
        # Zone 11+ : year-round growing
        if season == "Winter":
            for m in range(1, 13):
                add(m, "Grow indoors/greenhouse", "maintenance")
            add(1, "Start seeds", "start_indoors")
            add(4, "Start seeds", "start_indoors")
            add(7, "Start seeds", "start_indoors")
            add(10, "Start seeds", "start_indoors")
            add(3, "Harvest", "harvest")
            add(6, "Harvest", "harvest")
            add(9, "Harvest", "harvest")
            add(12, "Harvest", "harvest")
        else:
            add(1, "Plan & order seeds", "planning")
            for m in range(1, 13):
                add(m, "Direct sow (year-round zone)", "direct_sow")
            for m in range(3, 12):
                add(m, "Harvest", "harvest")
        return activities

    lf_month = _month_from_date(last_frost_date)
    ff_month = _month_from_date(first_frost_date)

    if season == "Spring":
        # Start indoors 6-8 weeks before last frost
        indoor_start = _weeks_before(last_frost_date, 8)
        indoor_end = _weeks_before(last_frost_date, 6)
        add(indoor_start.month, "Start seeds indoors", "start_indoors")
        if indoor_end.month != indoor_start.month:
            add(indoor_end.month, "Start seeds indoors", "start_indoors")

        # Planning 1-2 months before indoor start
        plan_month = _clamp_month(indoor_start.month - 1)
        add(plan_month, "Plan & order seeds", "planning")

        # Transplant after last frost
        add(lf_month, "Transplant outdoors", "transplant")
        next_month = _clamp_month(lf_month + 1)
        add(next_month, "Transplant outdoors", "transplant")

        # Maintenance during growing
        for m in range(lf_month, min(lf_month + 3, 13)):
            add(_clamp_month(m), "Water & maintain", "maintenance")

        # Harvest by mid-summer (June-July)
        harvest_start = _clamp_month(lf_month + 2)
        harvest_end = _clamp_month(lf_month + 3)
        add(harvest_start, "Harvest", "harvest")
        add(harvest_end, "Harvest", "harvest")

    elif season == "Summer":
        # Start indoors 4-6 weeks before last frost
        indoor_start = _weeks_before(last_frost_date, 6)
        indoor_end = _weeks_before(last_frost_date, 4)
        add(indoor_start.month, "Start seeds indoors", "start_indoors")
        if indoor_end.month != indoor_start.month:
            add(indoor_end.month, "Start seeds indoors", "start_indoors")

        # Planning
        plan_month = _clamp_month(indoor_start.month - 1)
        add(plan_month, "Plan & order seeds", "planning")

        # Transplant 2 weeks after last frost
        transplant_date = _weeks_after(last_frost_date, 2)
        add(transplant_date.month, "Transplant outdoors", "transplant")

        # Maintenance
        for m in range(transplant_date.month, min(transplant_date.month + 4, 13)):
            add(_clamp_month(m), "Water & maintain", "maintenance")

        # Harvest late summer to early fall
        harvest_start = _clamp_month(ff_month - 2)
        harvest_end = _clamp_month(ff_month - 1)
        add(harvest_start, "Harvest", "harvest")
        add(harvest_end, "Harvest", "harvest")
        add(ff_month, "Harvest", "harvest")

    elif season == "Fall":
        # Planning
        plan_month = _clamp_month(ff_month - 12 + 2) if ff_month >= 10 else _clamp_month(ff_month - 4)
        add(plan_month, "Plan & order seeds", "planning")

        # Direct sow 8-10 weeks before first frost
        sow_start = _weeks_before(first_frost_date, 10)
        sow_end = _weeks_before(first_frost_date, 8)
        add(sow_start.month, "Direct sow outdoors", "direct_sow")
        if sow_end.month != sow_start.month:
            add(sow_end.month, "Direct sow outdoors", "direct_sow")

        # Maintenance
        for m in range(sow_start.month, min(sow_start.month + 3, 13)):
            add(_clamp_month(m), "Water & maintain", "maintenance")

        # Harvest around first frost
        add(_clamp_month(ff_month - 1), "Harvest", "harvest")
        add(ff_month, "Harvest", "harvest")

    elif season == "Winter":
        # Can grow indoors/greenhouse year-round
        add(1, "Plan & order seeds", "planning")
        add(1, "Start seeds indoors/greenhouse", "start_indoors")
        add(4, "Start seeds indoors/greenhouse", "start_indoors")
        add(7, "Start seeds indoors/greenhouse", "start_indoors")
        add(10, "Start seeds indoors/greenhouse", "start_indoors")

        for m in range(1, 13):
            add(m, "Grow indoors/greenhouse", "maintenance")

        add(3, "Harvest", "harvest")
        add(6, "Harvest", "harvest")
        add(9, "Harvest", "harvest")
        add(12, "Harvest", "harvest")

    else:
        # Unknown season - add basic planning
        add(1, "Plan & order seeds", "planning")

    return activities


@planting_calendar_bp.route("", methods=["GET"])
def get_planting_calendar():
    """Return a month-by-month planting calendar for a given hardiness zone."""
    zone = request.args.get("zone")
    if not zone:
        return jsonify({"error": "The 'zone' query parameter is required."}), 400

    zone_num = parse_zone_number(zone)
    if zone_num is None:
        return jsonify({"error": f"Invalid zone: {zone}"}), 400

    # Determine frost dates
    year_round = False
    last_frost_date = None
    first_frost_date = None

    if zone_num >= 11:
        year_round = True
    else:
        lookup_zone = max(3, min(10, zone_num))
        data = FROST_DATA[lookup_zone]
        last_frost_date = date(CURRENT_YEAR, data["last_frost"][0], data["last_frost"][1])
        first_frost_date = date(CURRENT_YEAR, data["first_frost"][0], data["first_frost"][1])

    # Fetch all plants
    plants = Plant.query.all()

    # Build calendar structure: month -> activities
    calendar_months = {m: [] for m in range(1, 13)}

    for plant in plants:
        plant_activities = _generate_activities_for_plant(
            plant, last_frost_date, first_frost_date, year_round
        )
        for month, acts in plant_activities.items():
            for act in acts:
                calendar_months[month].append({
                    "plant_name": plant.name,
                    "plant_id": plant.id,
                    "activity": act["activity"],
                    "category": act["category"],
                })

    # Sort activities within each month by category then plant name
    category_order = {
        "planning": 0,
        "start_indoors": 1,
        "direct_sow": 2,
        "transplant": 3,
        "harvest": 4,
        "maintenance": 5,
    }

    calendar = []
    for m in range(1, 13):
        activities = sorted(
            calendar_months[m],
            key=lambda a: (category_order.get(a["category"], 99), a["plant_name"]),
        )
        calendar.append({
            "month": m,
            "month_name": MONTH_NAMES[m - 1],
            "activities": activities,
        })

    return jsonify({
        "zone": zone,
        "calendar": calendar,
        "current_month": 4,  # April 2026
    }), 200
