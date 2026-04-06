from datetime import date
from flask import Blueprint, request, jsonify
from .frost_dates import parse_zone_number, FROST_DATA

seasonal_tips_bp = Blueprint("seasonal_tips", __name__)

CURRENT_YEAR = 2026


def _get_season(month, zone_num):
    """Determine the gardening season based on month and zone.
    Returns one of: 'early_spring', 'spring', 'late_spring',
    'early_summer', 'summer', 'late_summer',
    'early_fall', 'fall', 'late_fall',
    'early_winter', 'winter', 'late_winter'.
    We simplify to four seasons for tips."""
    if zone_num >= 11:
        # Year-round growing zone
        if month in (12, 1, 2):
            return "winter"
        elif month in (3, 4, 5):
            return "spring"
        elif month in (6, 7, 8):
            return "summer"
        else:
            return "fall"

    lookup_zone = max(3, min(10, zone_num))
    data = FROST_DATA[lookup_zone]
    last_frost_month = data["last_frost"][0]
    first_frost_month = data["first_frost"][0]

    # Define seasons relative to frost dates
    if month <= last_frost_month - 2:
        return "winter"
    elif month <= last_frost_month:
        return "spring"
    elif month <= first_frost_month - 3:
        return "summer"
    elif month <= first_frost_month:
        return "fall"
    else:
        return "winter"


SEASONAL_TIPS = {
    "spring": {
        "title": "Spring Gardening Tips",
        "overview": "Spring is the busiest time in the garden. Focus on soil preparation, seed starting, and getting cool-season crops in the ground.",
        "tips": [
            {
                "category": "Soil Preparation",
                "items": [
                    "Test your soil pH and nutrient levels before planting. Amend as needed.",
                    "Work compost or aged manure into beds as soon as the soil can be worked.",
                    "Avoid working soil when it is too wet - squeeze a handful; if it crumbles, it is ready.",
                    "Top-dress perennial beds with 1-2 inches of compost.",
                    "Turn under any cover crops 2-3 weeks before planting."
                ]
            },
            {
                "category": "Seed Starting",
                "items": [
                    "Start warm-season crops (tomatoes, peppers, eggplant) indoors 6-8 weeks before last frost.",
                    "Use a heat mat for peppers and eggplant - they need soil temps of 75-85F to germinate.",
                    "Harden off seedlings by gradually exposing them to outdoor conditions over 7-10 days.",
                    "Label everything! It is easy to forget what you planted where.",
                    "Keep indoor seedlings under grow lights for 14-16 hours per day."
                ]
            },
            {
                "category": "Planting",
                "items": [
                    "Direct sow cool-season crops as soon as soil can be worked: peas, lettuce, spinach, radish.",
                    "Plant onion sets and seed potatoes 2-4 weeks before last frost.",
                    "Wait until after last frost to transplant warm-season crops outdoors.",
                    "Succession plant lettuce and radishes every 2 weeks for continuous harvest.",
                    "Plant bare-root trees, shrubs, and perennials while still dormant."
                ]
            },
            {
                "category": "Maintenance",
                "items": [
                    "Clean and sharpen garden tools before the busy season.",
                    "Remove winter mulch from perennial beds gradually as temperatures warm.",
                    "Divide overgrown perennials (hostas, daylilies, ornamental grasses).",
                    "Prune fruit trees and berry bushes while still dormant.",
                    "Set up trellises, cages, and supports before plants need them.",
                    "Start a compost pile if you do not have one."
                ]
            },
            {
                "category": "Pest Prevention",
                "items": [
                    "Install row covers over brassica seedlings to prevent cabbage moth damage.",
                    "Set out slug traps (beer traps or iron phosphate bait) early.",
                    "Encourage beneficial insects by planting early-blooming flowers.",
                    "Inspect overwintering perennials for signs of disease and remove affected material."
                ]
            }
        ]
    },
    "summer": {
        "title": "Summer Gardening Tips",
        "overview": "Summer is all about maintenance, harvesting, and keeping plants healthy through heat and drought. Stay on top of watering and pest management.",
        "tips": [
            {
                "category": "Watering",
                "items": [
                    "Water deeply and less frequently rather than shallow and often. Aim for 1 inch per week.",
                    "Water early in the morning to reduce evaporation and fungal disease.",
                    "Use drip irrigation or soaker hoses for efficient watering at the root zone.",
                    "Mulch beds with 2-3 inches of straw, wood chips, or leaves to retain moisture.",
                    "Container plants may need watering twice daily in extreme heat."
                ]
            },
            {
                "category": "Harvesting",
                "items": [
                    "Harvest vegetables regularly to encourage continued production.",
                    "Pick zucchini and summer squash when small (6-8 inches) for best flavor.",
                    "Harvest herbs in the morning for peak essential oil content.",
                    "Do not let cucumbers turn yellow on the vine - check daily.",
                    "Tomatoes taste best when harvested fully ripe on the vine.",
                    "Keep up with bean harvesting - pods left too long signal the plant to stop producing."
                ]
            },
            {
                "category": "Heat Management",
                "items": [
                    "Provide shade cloth (30-50%) for lettuce, spinach, and other greens.",
                    "Avoid fertilizing during extreme heat - it can stress plants.",
                    "Move container plants to afternoon shade during heat waves.",
                    "Expect blossom drop on tomatoes and peppers when temperatures exceed 90F.",
                    "Mist the garden in the evening to help plants cool down (but avoid wetting foliage on disease-prone plants)."
                ]
            },
            {
                "category": "Succession Planting",
                "items": [
                    "Plant fall crops in mid to late summer: broccoli, cabbage, kale, carrots, beets.",
                    "Start fall brassica seedlings indoors in July for transplanting in August.",
                    "Succession plant beans, cucumbers, and squash for late-season harvests.",
                    "Sow quick crops like radishes and lettuce in the shade of taller plants."
                ]
            },
            {
                "category": "Pest & Disease Management",
                "items": [
                    "Scout for tomato hornworms weekly - hand-pick and destroy.",
                    "Watch for squash vine borers - wrap lower stems with aluminum foil as prevention.",
                    "Remove and destroy any plants with signs of bacterial or viral disease.",
                    "Spray for powdery mildew with a baking soda solution (1 tbsp per gallon of water).",
                    "Release beneficial insects like ladybugs and lacewings for natural aphid control."
                ]
            }
        ]
    },
    "fall": {
        "title": "Fall Gardening Tips",
        "overview": "Fall is harvest season and time to prepare the garden for winter. Extend the season with row covers and cold frames, and get garlic in the ground.",
        "tips": [
            {
                "category": "Harvesting & Preserving",
                "items": [
                    "Harvest winter squash and pumpkins before hard frost. Cure in a warm spot for 2 weeks.",
                    "Pick green tomatoes before frost - ripen indoors on a sunny windowsill.",
                    "Dig sweet potatoes before the first frost.",
                    "Preserve excess harvest by canning, freezing, dehydrating, or fermenting.",
                    "Harvest herbs for drying before frost kills tender plants.",
                    "Make and freeze pesto, tomato sauce, and soup stocks from the harvest."
                ]
            },
            {
                "category": "Season Extension",
                "items": [
                    "Use row covers and cold frames to protect fall crops from early frosts.",
                    "Lettuce, spinach, kale, and carrots can survive light frosts with protection.",
                    "Cold frames extend the growing season by 4-6 weeks.",
                    "Leave root crops (carrots, parsnips, beets) in the ground under heavy mulch for winter harvest."
                ]
            },
            {
                "category": "Planting",
                "items": [
                    "Plant garlic cloves 6-8 weeks before the ground freezes.",
                    "Plant spring-blooming bulbs (tulips, daffodils, crocus) in October-November.",
                    "Sow cover crops (winter rye, crimson clover) in empty beds.",
                    "Plant bare-root trees and shrubs in fall for good root establishment.",
                    "Transplant or divide perennials while soil is still warm."
                ]
            },
            {
                "category": "Garden Cleanup",
                "items": [
                    "Remove spent annual plants and add disease-free material to compost.",
                    "Do NOT compost diseased plant material - dispose of it in the trash.",
                    "Clean and sanitize pots, trays, and tools.",
                    "Drain and store hoses before freezing weather.",
                    "Take notes on what worked and what did not this season for next year's planning."
                ]
            },
            {
                "category": "Soil Care",
                "items": [
                    "Add 2-3 inches of compost or aged manure to beds.",
                    "Apply lime to acidic soils in fall - it takes months to adjust pH.",
                    "Mulch beds with leaves or straw to protect soil over winter.",
                    "Get a soil test done now so you have results for spring planning."
                ]
            }
        ]
    },
    "winter": {
        "title": "Winter Gardening Tips",
        "overview": "Winter is the time for planning, learning, and preparation. Review last season, order seeds, and maintain tools and infrastructure.",
        "tips": [
            {
                "category": "Planning",
                "items": [
                    "Review your garden journal from the past season. Note successes and failures.",
                    "Draw a garden layout for next year, rotating crop families.",
                    "Order seeds early for the best selection - popular varieties sell out quickly.",
                    "Research new varieties to try. Look for disease resistance and climate suitability.",
                    "Plan your succession planting schedule."
                ]
            },
            {
                "category": "Learning",
                "items": [
                    "Take a master gardener course or attend gardening webinars.",
                    "Read gardening books and seed catalogs.",
                    "Join local gardening groups or online communities.",
                    "Learn a new preservation technique (fermenting, pressure canning, freeze-drying)."
                ]
            },
            {
                "category": "Indoor Growing",
                "items": [
                    "Grow microgreens on a sunny windowsill for fresh greens all winter.",
                    "Start an indoor herb garden under grow lights.",
                    "Force spring-blooming bulbs indoors for winter flowers.",
                    "Grow sprouts (alfalfa, mung bean, broccoli) for year-round nutrition.",
                    "Check stored potatoes, onions, and squash monthly - remove any that are spoiling."
                ]
            },
            {
                "category": "Tool & Infrastructure Maintenance",
                "items": [
                    "Clean, sharpen, and oil garden tools.",
                    "Repair or build raised beds, trellises, and cold frames.",
                    "Inventory your seed starting supplies - replace old grow lights and heat mats.",
                    "Service your mower, tiller, and other power equipment.",
                    "Build or repair compost bins."
                ]
            },
            {
                "category": "Winter Garden Care",
                "items": [
                    "Check mulch levels on perennial beds - add more if settling has exposed roots.",
                    "Brush heavy snow off evergreen branches to prevent breakage.",
                    "Avoid walking on frozen lawn - it damages grass crowns.",
                    "Monitor overwintering crops under cold frames and row covers.",
                    "Water evergreens during dry winter spells if the ground is not frozen."
                ]
            }
        ]
    },
}

# Zone-specific supplemental tips
ZONE_SPECIFIC_TIPS = {
    "spring": {
        "cold": [  # Zones 3-5
            "Be patient - your last frost date is later than you think. Do not rush warm-season transplants.",
            "Use Wall O' Waters or cloches to get a head start on tomatoes and peppers.",
            "Choose short-season varieties (days to maturity under 70 days) for reliable harvests.",
            "Start seeds indoors under lights - your outdoor growing season is too short for many crops started outdoors.",
        ],
        "moderate": [  # Zones 6-7
            "You have a good balance of season length. Most crops will succeed with proper timing.",
            "Consider starting a few warm-season crops indoors while direct-sowing cool-season crops.",
            "Watch for late cold snaps - have row covers ready for unexpected frost.",
        ],
        "warm": [  # Zones 8-10
            "You can start planting cool-season crops very early - some may already be harvestable.",
            "Get warm-season transplants in the ground by mid-spring to beat the summer heat.",
            "Plant quick-maturing crops that finish before the hottest months.",
        ],
        "tropical": [  # Zones 11+
            "You can plant year-round! Focus on what is best suited to the current dry or wet season.",
            "Many temperate crops struggle in your heat - focus on tropical varieties.",
            "Provide shade for cool-season crops like lettuce and spinach.",
        ],
    },
    "summer": {
        "cold": [
            "Your short summer means every warm day counts. Prioritize heat-loving crops.",
            "Use black plastic mulch to warm soil for melons and peppers.",
            "Enjoy your peak growing season - most of your harvest comes in the next 8-10 weeks.",
        ],
        "moderate": [
            "Mulch heavily to conserve moisture during the hottest weeks.",
            "Start thinking about fall planting now - start brassica seeds indoors.",
            "Provide afternoon shade for lettuce and other greens to prevent bolting.",
        ],
        "warm": [
            "Heat is your biggest challenge. Water deeply and mulch everything.",
            "Many crops slow production above 90F. Focus on heat-loving crops like okra, sweet potatoes, and peppers.",
            "Plant fall tomatoes in mid-summer for a second harvest.",
        ],
        "tropical": [
            "Watch for tropical storms and heavy rain - ensure good drainage.",
            "This may be your off-season for some crops. Focus on heat-tolerant varieties.",
            "Monitor for increased pest and disease pressure in the heat and humidity.",
        ],
    },
    "fall": {
        "cold": [
            "Your first frost comes early. Harvest everything before it hits.",
            "Use cold frames and row covers aggressively to extend your season.",
            "Get garlic planted - it needs to establish roots before the ground freezes.",
            "Mulch perennial beds heavily (6+ inches) before the ground freezes solid.",
        ],
        "moderate": [
            "You have a nice fall growing window. Take advantage of it for cool-season crops.",
            "Fall is an excellent time to plant garlic, shallots, and spring-blooming bulbs.",
            "Sow cover crops in any empty beds to protect and build soil over winter.",
        ],
        "warm": [
            "Fall is your second spring! Plant cool-season crops for winter harvest.",
            "Lettuce, broccoli, kale, carrots, and peas all thrive in your fall garden.",
            "Take advantage of the cooler temperatures - many crops actually prefer fall conditions.",
        ],
        "tropical": [
            "This is often the start of the prime growing season for cool-season crops.",
            "Monitor for lingering summer pests as temperatures begin to moderate.",
            "Great time to plant most vegetables in your zone.",
        ],
    },
    "winter": {
        "cold": [
            "Your garden is dormant. Focus entirely on planning and indoor activities.",
            "Check on overwintering garlic under the mulch.",
            "Clean the greenhouse and start planning your seed-starting schedule.",
            "Order seeds in January - many popular varieties sell out by February.",
        ],
        "moderate": [
            "Some cold-hardy crops may still be harvestable under row covers.",
            "Start planning and seed ordering by mid-winter.",
            "Begin indoor seed starting 8-10 weeks before your last frost date.",
        ],
        "warm": [
            "Winter is an excellent growing season for you. Plant cool-season crops now.",
            "Cover crops are not as critical in your zone, but they still benefit soil.",
            "Prune deciduous fruit trees while dormant.",
        ],
        "tropical": [
            "Dry season may be your best planting time. Take advantage of moderate temperatures.",
            "Many temperate vegetables grow well now: tomatoes, peppers, beans.",
            "This is your prime gardening season for most crops.",
        ],
    },
}


def _get_zone_category(zone_num):
    """Categorize zone for zone-specific tips."""
    if zone_num >= 11:
        return "tropical"
    elif zone_num >= 8:
        return "warm"
    elif zone_num >= 6:
        return "moderate"
    else:
        return "cold"


@seasonal_tips_bp.route("", methods=["GET"])
def get_seasonal_tips():
    """Return seasonal gardening tips based on the current date and user's zone.

    Query params:
        zone (required): USDA hardiness zone (e.g. '7a', '5b')
        month (optional): Override the current month (1-12) for testing
    """
    zone = request.args.get("zone")
    if not zone:
        return jsonify({"error": "The 'zone' query parameter is required."}), 400

    zone_num = parse_zone_number(zone)
    if zone_num is None:
        return jsonify({"error": f"Invalid zone: {zone}"}), 400

    # Allow month override for testing
    month_param = request.args.get("month")
    if month_param:
        try:
            current_month = int(month_param)
            if not 1 <= current_month <= 12:
                return jsonify({"error": "Month must be between 1 and 12."}), 400
        except ValueError:
            return jsonify({"error": "Month must be a number."}), 400
    else:
        current_month = date.today().month

    season = _get_season(current_month, zone_num)
    zone_category = _get_zone_category(zone_num)

    base_tips = SEASONAL_TIPS.get(season, SEASONAL_TIPS["spring"])
    zone_tips = ZONE_SPECIFIC_TIPS.get(season, {}).get(zone_category, [])

    # Compute frost date info for context
    frost_info = {}
    if zone_num >= 11:
        frost_info = {"year_round": True, "note": "Year-round growing zone - no frost dates."}
    else:
        lookup_zone = max(3, min(10, zone_num))
        data = FROST_DATA[lookup_zone]
        last_frost = date(CURRENT_YEAR, data["last_frost"][0], data["last_frost"][1])
        first_frost = date(CURRENT_YEAR, data["first_frost"][0], data["first_frost"][1])
        frost_info = {
            "year_round": False,
            "last_frost": last_frost.isoformat(),
            "first_frost": first_frost.isoformat(),
            "growing_season_days": (first_frost - last_frost).days,
        }

    return jsonify({
        "zone": zone,
        "month": current_month,
        "month_name": MONTH_NAMES[current_month - 1] if 1 <= current_month <= 12 else "Unknown",
        "season": season,
        "frost_dates": frost_info,
        "title": base_tips["title"],
        "overview": base_tips["overview"],
        "tips": base_tips["tips"],
        "zone_specific_tips": zone_tips,
    }), 200


MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
