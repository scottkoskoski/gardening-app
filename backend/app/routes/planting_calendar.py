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


# ---------------------------------------------------------------------------
# Plant-type classification for more accurate calendar generation
# ---------------------------------------------------------------------------
COOL_SEASON_CROPS = {
    "Pea", "Sugar Snap Pea", "Lettuce", "Romaine Lettuce", "Spinach", "Arugula",
    "Radish", "Carrot", "Beet", "Turnip", "Kale", "Broccoli", "Cabbage",
    "Cauliflower", "Brussels Sprouts", "Collard Greens", "Swiss Chard",
    "Bok Choy", "Kohlrabi", "Endive", "Radicchio", "Parsnip", "Celery",
    "Celery Root", "Onion", "Green Onion", "Leek", "Garlic", "Rhubarb",
    "Romanesco",
}

WARM_SEASON_CROPS = {
    "Tomato", "Cherry Tomato", "Pepper", "Bell Pepper", "Hot Pepper",
    "Jalapeno Pepper", "Eggplant", "Cucumber", "Squash", "Zucchini",
    "Butternut Squash", "Winter Squash", "Pumpkin", "Watermelon", "Cantaloupe",
    "Corn", "Green Bean", "Okra", "Sweet Potato", "Tomatillo", "Ground Cherry",
    "Edamame",
}

PERENNIAL_CROPS = {
    "Asparagus", "Strawberry", "Blueberry", "Raspberry", "Blackberry",
    "Rhubarb", "Grape", "Fig", "Artichoke", "Horseradish", "Sunchoke",
    "Comfrey", "Passion Fruit", "Lemon", "Avocado",
}

HERBS = {
    "Basil", "Cilantro", "Dill", "Parsley", "Rosemary", "Sage", "Thyme",
    "Oregano", "Mint", "Peppermint", "Chives", "Tarragon", "Marjoram",
    "Lavender", "Lemon Balm", "Lovage", "Sorrel", "Bay Laurel", "Borage",
    "Chamomile", "Stevia", "Lemongrass",
}

TENDER_HERBS = {"Basil", "Cilantro", "Dill", "Lemongrass", "Stevia"}
HARDY_HERBS = {"Rosemary", "Sage", "Thyme", "Oregano", "Chives", "Lavender",
               "Tarragon", "Lovage", "Sorrel", "Bay Laurel", "Marjoram",
               "Lemon Balm", "Peppermint", "Mint", "Chamomile"}

FLOWERS = {
    "Marigold", "Nasturtium", "Sunflower", "Zinnia", "Cosmos", "Calendula",
    "Petunia", "Pansy", "Snapdragon", "Geranium", "Begonia", "Impatiens",
    "Dahlia", "Chrysanthemum", "Rose", "Peony", "Lily", "Daylily",
    "Hosta", "Hydrangea", "Clematis", "Morning Glory", "Sweet Pea",
    "Coneflower", "Echinacea", "Black-Eyed Susan", "Crocus", "Daffodil",
    "Tulip",
}

DIRECT_SOW_PREFERRED = {
    "Carrot", "Radish", "Beet", "Pea", "Sugar Snap Pea", "Green Bean",
    "Corn", "Cucumber", "Squash", "Zucchini", "Pumpkin", "Watermelon",
    "Cantaloupe", "Turnip", "Parsnip", "Arugula", "Spinach", "Dill",
    "Cilantro", "Nasturtium", "Sunflower", "Borage", "Morning Glory",
}

TRANSPLANT_PREFERRED = {
    "Tomato", "Cherry Tomato", "Pepper", "Bell Pepper", "Hot Pepper",
    "Jalapeno Pepper", "Eggplant", "Broccoli", "Cabbage", "Cauliflower",
    "Brussels Sprouts", "Celery", "Celery Root", "Leek", "Artichoke",
    "Tomatillo", "Ground Cherry", "Okra",
}

# Crops that can handle a fall planting for overwintering or late harvest
FALL_PLANTABLE = {
    "Garlic", "Onion", "Kale", "Collard Greens", "Spinach", "Lettuce",
    "Romaine Lettuce", "Arugula", "Radish", "Turnip", "Beet", "Carrot",
    "Pea", "Sugar Snap Pea", "Broccoli", "Cabbage", "Cauliflower",
    "Brussels Sprouts", "Swiss Chard", "Bok Choy", "Endive", "Radicchio",
    "Kohlrabi",
}


def _classify_plant(plant_name):
    """Return a classification label for the plant."""
    if plant_name in COOL_SEASON_CROPS:
        return "cool_season"
    if plant_name in WARM_SEASON_CROPS:
        return "warm_season"
    if plant_name in PERENNIAL_CROPS:
        return "perennial"
    if plant_name in TENDER_HERBS:
        return "tender_herb"
    if plant_name in HARDY_HERBS:
        return "hardy_herb"
    if plant_name in FLOWERS:
        return "flower"
    if plant_name == "Microgreens":
        return "microgreens"
    if plant_name == "Cover Crop Mix":
        return "cover_crop"
    if plant_name == "Ginger" or plant_name == "Turmeric":
        return "tropical"
    return "unknown"


def _generate_activities_for_plant(plant, last_frost_date, first_frost_date, year_round):
    """Generate month-keyed activities for a single plant based on its type and zone frost dates."""
    activities = {}

    def add(month, activity, category):
        m = _clamp_month(month)
        activities.setdefault(m, []).append({"activity": activity, "category": category})

    name = plant.name
    classification = _classify_plant(name)

    # ------- Year-round zones (11+) -------
    if year_round:
        if classification == "microgreens":
            for m in range(1, 13):
                add(m, "Sow microgreens indoors (year-round)", "direct_sow")
            return activities

        if classification == "cover_crop":
            add(9, "Sow cover crop", "direct_sow")
            add(10, "Sow cover crop", "direct_sow")
            return activities

        if classification == "tropical":
            add(1, "Plant rhizomes", "direct_sow")
            add(2, "Plant rhizomes", "direct_sow")
            for m in range(3, 11):
                add(m, "Maintain and water", "maintenance")
            add(10, "Harvest", "harvest")
            add(11, "Harvest", "harvest")
            return activities

        # General year-round approach
        add(1, "Plan and order seeds", "planning")
        for m in range(1, 13):
            add(m, "Direct sow or transplant (year-round zone)", "direct_sow")
        for m in range(3, 12):
            add(m, "Harvest", "harvest")
        return activities

    lf_month = _month_from_date(last_frost_date)
    ff_month = _month_from_date(first_frost_date)

    # ------- Microgreens -------
    if classification == "microgreens":
        for m in range(1, 13):
            add(m, "Sow microgreens indoors (year-round)", "direct_sow")
        return activities

    # ------- Cover Crop -------
    if classification == "cover_crop":
        add(_clamp_month(ff_month - 1), "Sow cover crop after harvest", "direct_sow")
        add(ff_month, "Sow cover crop after harvest", "direct_sow")
        add(_clamp_month(lf_month - 1), "Turn under cover crop before planting", "maintenance")
        return activities

    # ------- Tropical (Ginger, Turmeric) -------
    if classification == "tropical":
        indoor_start = _clamp_month(lf_month - 2)
        add(indoor_start, "Start rhizomes indoors in pots", "start_indoors")
        transplant_month = _clamp_month(lf_month + 1)
        add(transplant_month, "Move outdoors after frost danger passes", "transplant")
        for m in range(transplant_month, min(transplant_month + 4, 13)):
            add(_clamp_month(m), "Water and maintain", "maintenance")
        add(_clamp_month(ff_month - 1), "Harvest before frost", "harvest")
        return activities

    # ------- Cool Season Crops -------
    if classification == "cool_season":
        # Planning
        plan_month = _clamp_month(lf_month - 3)
        add(plan_month, "Plan and order seeds", "planning")

        if name in TRANSPLANT_PREFERRED:
            # Start indoors 6-8 weeks before last frost
            indoor_start = _weeks_before(last_frost_date, 8)
            add(indoor_start.month, "Start seeds indoors", "start_indoors")
            # Transplant 2-4 weeks before last frost (cool season crops handle light frost)
            transplant_date = _weeks_before(last_frost_date, 3)
            add(transplant_date.month, "Transplant outdoors (can tolerate light frost)", "transplant")
        elif name in DIRECT_SOW_PREFERRED:
            # Direct sow 2-4 weeks before last frost
            sow_date = _weeks_before(last_frost_date, 4)
            add(sow_date.month, "Direct sow outdoors", "direct_sow")
            if sow_date.month != _weeks_before(last_frost_date, 2).month:
                add(_weeks_before(last_frost_date, 2).month, "Direct sow outdoors", "direct_sow")
        elif name == "Garlic":
            # Garlic is planted in fall for spring harvest
            add(_clamp_month(ff_month - 1), "Plant garlic cloves (fall planting)", "direct_sow")
            add(ff_month, "Plant garlic cloves (fall planting)", "direct_sow")
            add(_clamp_month(lf_month + 1), "Remove scapes when they curl", "maintenance")
            add(_clamp_month(lf_month + 2), "Harvest when lower leaves brown", "harvest")
            add(_clamp_month(lf_month + 3), "Harvest when lower leaves brown", "harvest")
            return activities
        else:
            # Default cool season: sow around last frost
            sow_date = _weeks_before(last_frost_date, 3)
            add(sow_date.month, "Sow or transplant outdoors", "direct_sow")

        # Maintenance during spring growing period
        for m in range(lf_month, min(lf_month + 3, 13)):
            add(_clamp_month(m), "Water, weed, and monitor for pests", "maintenance")

        # Harvest in late spring / early summer
        harvest_start = _clamp_month(lf_month + 1)
        harvest_end = _clamp_month(lf_month + 3)
        add(harvest_start, "Begin harvesting", "harvest")
        add(harvest_end, "Harvest", "harvest")

        # Fall planting opportunity
        if name in FALL_PLANTABLE:
            fall_sow = _weeks_before(first_frost_date, 8)
            add(fall_sow.month, f"Sow fall crop of {name}", "direct_sow")
            add(_clamp_month(ff_month - 1), "Harvest fall crop", "harvest")
            add(ff_month, "Harvest fall crop or protect with row cover", "harvest")

        return activities

    # ------- Warm Season Crops -------
    if classification == "warm_season":
        # Planning
        plan_month = _clamp_month(lf_month - 3)
        add(plan_month, "Plan and order seeds", "planning")

        if name in TRANSPLANT_PREFERRED:
            # Start indoors 6-8 weeks before last frost
            indoor_start = _weeks_before(last_frost_date, 8)
            indoor_end = _weeks_before(last_frost_date, 6)
            add(indoor_start.month, "Start seeds indoors", "start_indoors")
            if indoor_end.month != indoor_start.month:
                add(indoor_end.month, "Start seeds indoors", "start_indoors")

            # Transplant 1-2 weeks after last frost
            transplant_date = _weeks_after(last_frost_date, 2)
            add(transplant_date.month, "Transplant outdoors after last frost", "transplant")
        elif name in DIRECT_SOW_PREFERRED:
            # Direct sow 1-2 weeks after last frost when soil is warm
            sow_date = _weeks_after(last_frost_date, 1)
            add(sow_date.month, "Direct sow outdoors (soil must be warm)", "direct_sow")
            if name == "Corn":
                add(sow_date.month, "Plant in blocks of 4+ rows for pollination", "direct_sow")
        elif name == "Sweet Potato":
            # Sweet potatoes: plant slips after soil warms
            add(_clamp_month(lf_month + 1), "Plant sweet potato slips in warm soil", "transplant")
        else:
            sow_date = _weeks_after(last_frost_date, 1)
            add(sow_date.month, "Sow or transplant outdoors", "direct_sow")

        # Maintenance during the warm season
        for m in range(lf_month + 1, min(ff_month, 13)):
            add(_clamp_month(m), "Water deeply, mulch, and monitor for pests", "maintenance")

        # Fertilizing
        fert_month = _clamp_month(lf_month + 2)
        add(fert_month, "Side-dress with compost or fertilizer", "maintenance")

        # Harvest period depends on the crop
        if name in {"Watermelon", "Cantaloupe", "Pumpkin", "Butternut Squash", "Winter Squash"}:
            # Late harvest crops
            add(_clamp_month(ff_month - 2), "Check for ripeness", "harvest")
            add(_clamp_month(ff_month - 1), "Harvest before frost", "harvest")
        elif name == "Sweet Potato":
            add(_clamp_month(ff_month - 1), "Harvest before first frost", "harvest")
        else:
            # Standard warm season harvest
            harvest_start = _clamp_month(lf_month + 2)
            harvest_end = _clamp_month(ff_month - 1)
            add(harvest_start, "Begin harvesting", "harvest")
            if harvest_end > harvest_start:
                add(harvest_end, "Continue harvesting", "harvest")
            add(ff_month, "Final harvest before frost", "harvest")

        return activities

    # ------- Perennial Crops -------
    if classification == "perennial":
        add(1, "Review and order new varieties", "planning")

        if name in {"Strawberry"}:
            add(lf_month, "Plant new strawberry plants or uncover overwintered beds", "transplant")
            add(_clamp_month(lf_month + 1), "Remove old mulch, fertilize", "maintenance")
            for m in range(lf_month + 1, min(lf_month + 4, 13)):
                add(_clamp_month(m), "Water and maintain; remove runners if desired", "maintenance")
            add(_clamp_month(lf_month + 2), "Harvest (June-bearing types)", "harvest")
            add(_clamp_month(lf_month + 3), "Harvest (everbearing types)", "harvest")
            add(_clamp_month(ff_month - 1), "Renovate June-bearing beds", "maintenance")
            add(ff_month, "Mulch for winter protection", "maintenance")
        elif name in {"Blueberry", "Raspberry", "Blackberry", "Grape"}:
            add(2, "Prune while dormant", "maintenance")
            add(3, "Prune while dormant", "maintenance")
            add(lf_month, "Fertilize and mulch", "maintenance")
            for m in range(lf_month + 1, min(lf_month + 4, 13)):
                add(_clamp_month(m), "Water deeply during fruit development", "maintenance")
            add(_clamp_month(lf_month + 2), "Begin harvesting fruit", "harvest")
            add(_clamp_month(lf_month + 3), "Harvest fruit", "harvest")
            add(_clamp_month(lf_month + 4), "Harvest fruit", "harvest")
            add(11, "Mulch for winter protection", "maintenance")
        elif name == "Asparagus":
            add(lf_month, "Fertilize established beds", "maintenance")
            add(_clamp_month(lf_month + 1), "Harvest spears (year 3+ only)", "harvest")
            add(_clamp_month(lf_month + 2), "Harvest spears; stop by early summer", "harvest")
            for m in range(lf_month + 3, min(ff_month + 1, 13)):
                add(_clamp_month(m), "Let ferns grow to build root strength", "maintenance")
            add(12, "Cut back dead ferns after hard frost", "maintenance")
        elif name == "Rhubarb":
            add(lf_month, "Fertilize crowns with compost", "maintenance")
            add(_clamp_month(lf_month + 1), "Harvest stalks (year 3+ only)", "harvest")
            add(_clamp_month(lf_month + 2), "Harvest stalks; stop by late June", "harvest")
            add(_clamp_month(lf_month + 3), "Let plants rebuild energy", "maintenance")
            add(11, "Mulch with compost for winter", "maintenance")
        elif name == "Fig":
            add(_clamp_month(lf_month - 1), "Uncover/unwrap winter protection", "maintenance")
            add(lf_month, "Prune dead branches and fertilize", "maintenance")
            add(_clamp_month(lf_month + 3), "Harvest early figs (breba crop)", "harvest")
            add(_clamp_month(ff_month - 2), "Harvest main crop figs", "harvest")
            add(_clamp_month(ff_month - 1), "Harvest remaining figs", "harvest")
            add(ff_month, "Wrap or protect tree for winter (cold zones)", "maintenance")
        elif name == "Sunchoke":
            add(lf_month, "Plant tubers", "direct_sow")
            for m in range(lf_month + 1, min(ff_month, 13)):
                add(_clamp_month(m), "Maintain - water in dry periods", "maintenance")
            add(ff_month, "Harvest tubers after frost", "harvest")
            add(_clamp_month(ff_month + 1), "Harvest through winter as needed", "harvest")
        elif name == "Horseradish":
            add(lf_month, "Plant root cuttings", "direct_sow")
            for m in range(lf_month + 1, min(ff_month, 13)):
                add(_clamp_month(m), "Maintain - remove flower stalks", "maintenance")
            add(ff_month, "Harvest roots after frost for strongest flavor", "harvest")
        else:
            # General perennial
            add(lf_month, "Plant or uncover perennials", "transplant")
            add(_clamp_month(lf_month + 1), "Fertilize and mulch", "maintenance")
            for m in range(lf_month + 2, min(ff_month, 13)):
                add(_clamp_month(m), "Maintain and water as needed", "maintenance")
            add(_clamp_month(ff_month - 1), "Harvest if applicable", "harvest")
            add(ff_month, "Prepare for winter dormancy", "maintenance")

        return activities

    # ------- Tender Herbs -------
    if classification == "tender_herb":
        plan_month = _clamp_month(lf_month - 2)
        add(plan_month, "Plan and order seeds", "planning")

        if name == "Basil":
            indoor_start = _weeks_before(last_frost_date, 6)
            add(indoor_start.month, "Start seeds indoors", "start_indoors")
            transplant_date = _weeks_after(last_frost_date, 1)
            add(transplant_date.month, "Transplant outdoors after frost danger passes", "transplant")
        elif name in {"Cilantro", "Dill"}:
            # Cool-season herbs that bolt in heat
            sow_date = _weeks_before(last_frost_date, 2)
            add(sow_date.month, "Direct sow outdoors", "direct_sow")
            add(_clamp_month(lf_month + 1), "Succession sow every 2-3 weeks", "direct_sow")
            # Fall sowing
            fall_sow = _weeks_before(first_frost_date, 8)
            add(fall_sow.month, "Sow fall crop", "direct_sow")
        else:
            sow_date = _weeks_after(last_frost_date, 1)
            add(sow_date.month, "Sow or transplant outdoors after frost", "direct_sow")

        for m in range(lf_month + 1, min(ff_month, 13)):
            add(_clamp_month(m), "Harvest regularly to encourage growth", "maintenance")

        add(_clamp_month(lf_month + 1), "Begin harvesting leaves", "harvest")
        add(_clamp_month(ff_month - 2), "Harvest and preserve before frost", "harvest")
        add(_clamp_month(ff_month - 1), "Final harvest before frost; bring potted plants indoors", "harvest")

        return activities

    # ------- Hardy Herbs -------
    if classification == "hardy_herb":
        add(1, "Review herb garden plans", "planning")

        if name in {"Mint", "Peppermint"}:
            add(lf_month, "Plant in containers (invasive - do not plant in ground)", "transplant")
        elif name == "Lavender":
            add(lf_month, "Plant new lavender in well-drained soil", "transplant")
            add(_clamp_month(lf_month + 1), "Prune by one-third after new growth starts", "maintenance")
        elif name == "Rosemary":
            add(lf_month, "Uncover or move outdoors after frost danger", "maintenance")
            add(ff_month, "Bring potted rosemary indoors before frost (zones below 7)", "maintenance")
        else:
            add(lf_month, "Plant or divide perennial herbs", "transplant")

        for m in range(lf_month + 1, min(ff_month, 13)):
            add(_clamp_month(m), "Harvest regularly", "harvest")

        add(_clamp_month(ff_month - 1), "Take cuttings for indoor growing", "maintenance")
        add(ff_month, "Mulch perennial herbs for winter protection", "maintenance")

        return activities

    # ------- Flowers -------
    if classification == "flower":
        add(1, "Plan flower garden and order seeds/bulbs", "planning")

        # Spring-planted bulbs and perennials
        if name in {"Dahlia", "Lily", "Gladiolus"}:
            add(lf_month, "Plant bulbs/tubers after last frost", "direct_sow")
            for m in range(lf_month + 1, min(ff_month, 13)):
                add(_clamp_month(m), "Water and stake as needed", "maintenance")
            add(_clamp_month(ff_month - 1), "Enjoy blooms; deadhead for more flowers", "harvest")
            add(ff_month, "Dig up tender bulbs before hard frost for storage", "maintenance")
        # Fall-planted bulbs
        elif name in {"Crocus", "Daffodil", "Tulip"}:
            add(_clamp_month(ff_month - 1), "Plant bulbs in fall", "direct_sow")
            add(ff_month, "Plant bulbs in fall", "direct_sow")
            add(_clamp_month(lf_month - 1), "Enjoy early spring blooms", "harvest")
            add(lf_month, "Enjoy blooms; let foliage die back naturally", "harvest")
        # Hardy perennial flowers
        elif name in {"Rose", "Peony", "Hydrangea", "Clematis", "Hosta",
                       "Daylily", "Coneflower", "Echinacea", "Black-Eyed Susan"}:
            add(lf_month, "Plant or divide perennials", "transplant")
            add(_clamp_month(lf_month + 1), "Fertilize and mulch", "maintenance")
            for m in range(lf_month + 2, min(ff_month, 13)):
                add(_clamp_month(m), "Deadhead and maintain", "maintenance")
            add(_clamp_month(lf_month + 2), "Enjoy blooms", "harvest")
            add(_clamp_month(lf_month + 3), "Enjoy blooms", "harvest")
            add(11, "Cut back and mulch for winter", "maintenance")
        # Cool-season annuals
        elif name in {"Pansy", "Snapdragon", "Sweet Pea", "Calendula"}:
            sow_date = _weeks_before(last_frost_date, 4)
            add(sow_date.month, "Start seeds indoors or direct sow (frost-tolerant)", "start_indoors")
            add(lf_month, "Transplant outdoors", "transplant")
            add(_clamp_month(lf_month + 1), "Enjoy blooms", "harvest")
            add(_clamp_month(lf_month + 2), "Enjoy blooms; deadhead regularly", "harvest")
            # Fall re-planting for mild climates
            add(_clamp_month(ff_month - 2), "Plant fall crop for cool-season color", "direct_sow")
        # Warm-season annuals
        else:
            indoor_start = _weeks_before(last_frost_date, 6)
            add(indoor_start.month, "Start seeds indoors or purchase transplants", "start_indoors")
            transplant_date = _weeks_after(last_frost_date, 1)
            add(transplant_date.month, "Transplant outdoors after frost", "transplant")
            for m in range(transplant_date.month, min(ff_month, 13)):
                add(_clamp_month(m), "Deadhead for continuous blooms", "maintenance")
            add(_clamp_month(lf_month + 2), "Enjoy blooms", "harvest")
            add(_clamp_month(ff_month - 2), "Enjoy blooms", "harvest")
            add(ff_month, "Remove spent plants; save seeds", "maintenance")

        return activities

    # ------- Unknown / Default -------
    season = (plant.growing_season or "").strip()

    if season == "Spring":
        indoor_start = _weeks_before(last_frost_date, 8)
        add(indoor_start.month, "Start seeds indoors", "start_indoors")
        add(_clamp_month(indoor_start.month - 1), "Plan and order seeds", "planning")
        add(lf_month, "Transplant or direct sow outdoors", "transplant")
        for m in range(lf_month, min(lf_month + 3, 13)):
            add(_clamp_month(m), "Water and maintain", "maintenance")
        add(_clamp_month(lf_month + 2), "Harvest", "harvest")
        add(_clamp_month(lf_month + 3), "Harvest", "harvest")
    elif season == "Summer":
        indoor_start = _weeks_before(last_frost_date, 6)
        add(indoor_start.month, "Start seeds indoors", "start_indoors")
        add(_clamp_month(indoor_start.month - 1), "Plan and order seeds", "planning")
        transplant_date = _weeks_after(last_frost_date, 2)
        add(transplant_date.month, "Transplant outdoors", "transplant")
        for m in range(transplant_date.month, min(transplant_date.month + 4, 13)):
            add(_clamp_month(m), "Water and maintain", "maintenance")
        add(_clamp_month(ff_month - 2), "Harvest", "harvest")
        add(_clamp_month(ff_month - 1), "Harvest", "harvest")
    elif season == "Fall":
        sow_start = _weeks_before(first_frost_date, 10)
        add(_clamp_month(sow_start.month - 1), "Plan and order seeds", "planning")
        add(sow_start.month, "Direct sow outdoors", "direct_sow")
        for m in range(sow_start.month, min(sow_start.month + 3, 13)):
            add(_clamp_month(m), "Water and maintain", "maintenance")
        add(_clamp_month(ff_month - 1), "Harvest", "harvest")
        add(ff_month, "Harvest", "harvest")
    elif season == "Winter":
        add(1, "Plan and order seeds", "planning")
        add(1, "Start seeds indoors/greenhouse", "start_indoors")
        for m in range(1, 13):
            add(m, "Grow indoors/greenhouse", "maintenance")
        add(3, "Harvest", "harvest")
        add(6, "Harvest", "harvest")
        add(9, "Harvest", "harvest")
        add(12, "Harvest", "harvest")
    else:
        add(1, "Plan and order seeds", "planning")

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
