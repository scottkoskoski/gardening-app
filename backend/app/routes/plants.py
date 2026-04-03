import logging
from flask import Blueprint, request, jsonify
from ..models.database import db
from ..models.plant import Plant, PlantSchema
from .garden_map import COMPANION_DATA

plants_bp = Blueprint("plants", __name__)
logger = logging.getLogger(__name__)

OPENFARM_BASE_URL = "https://openfarm.cc"


def _normalize_image_url(url):
    """Convert relative OpenFarm image paths to absolute URLs."""
    if url and url.startswith("/"):
        return OPENFARM_BASE_URL + url
    return url


# Creating instance of PlantSchema
plant_schema = PlantSchema()
plants_schema = PlantSchema(many=True) # For serializing multiple plants

@plants_bp.route("/get_plants", methods=["GET"])
def get_plants():
    """Fetches plant recommendations based on filters from the database."""
    hardiness_zone = request.args.get("zone") # User's hardiness zone
    greenhouse = request.args.get("greenhouse", "false").lower() == "true" # Convert to boolean
    container_gardening = request.args.get("containers", "false").lower() == "true" # Convert to boolean

    # New filter params
    search = request.args.get("search", "").strip()
    sunlight = request.args.get("sunlight", "").strip()
    water_needs = request.args.get("water_needs", "").strip()
    growing_season = request.args.get("growing_season", "").strip()
    space_required = request.args.get("space_required", "").strip()
    sowing_method = request.args.get("sowing_method", "").strip()

    # Starting with all plants
    query = Plant.query

    # Apply filters
    if hardiness_zone:
        query = query.filter(
            Plant.hardiness_min <= hardiness_zone,
            Plant.hardiness_max >= hardiness_zone,
        )

    if greenhouse:
        query = query.filter(Plant.requires_greenhouse == True)

    if container_gardening:
        query = query.filter(Plant.suitable_for_containers == True)

    if search:
        query = query.filter(Plant.name.ilike(f"%{search}%"))

    if sunlight:
        query = query.filter(Plant.sunlight == sunlight)

    if water_needs:
        query = query.filter(Plant.water_needs == water_needs)

    if growing_season:
        query = query.filter(Plant.growing_season == growing_season)

    if space_required:
        query = query.filter(Plant.space_required == space_required)

    if sowing_method:
        query = query.filter(Plant.sowing_method == sowing_method)

    # Fetch filtered plants
    plants = query.all()

    result = plants_schema.dump(plants)

    # Format data for JSON response
    plants_data = []
    for plant in result:
        plants_data.append({
            "id": plant.get("id"),
            "name": plant.get("name"),
            "description": plant.get("description", "No description available."),
            "hardinessMin": plant.get("hardiness_min", "N/A"),
            "hardinessMax": plant.get("hardiness_max", "N/A"),
            "requiresGreenhouse": plant.get("requires_greenhouse", False),
            "suitableForContainers": plant.get("suitable_for_containers", False),
            "growingSeason": plant.get("growing_season", "N/A"),
            "waterNeeds": plant.get("water_needs", "N/A"),
            "sunlight": plant.get("sunlight", "N/A"),
            "spaceRequired": plant.get("space_required", "N/A"),
            "imageUrl": _normalize_image_url(plant.get("image_url")),
        })

    return jsonify({"plants": plants_data})

@plants_bp.route("/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    """Retrieves a specific plant by ID."""
    plant = Plant.query.get_or_404(plant_id)
    
    # Using schema to serialize a single plant
    result = plant_schema.dump(plant)
    
    plant_name = result.get("name", "")
    companion_info = COMPANION_DATA.get(plant_name, {})
    companions = {
        "good": companion_info.get("good", []),
        "bad": companion_info.get("bad", []),
        "tips": companion_info.get("tips", "")
    }

    plant_data = {
            "id": result.get("id"),
            "name": result.get("name"),
            "scientificName": result.get("scientific_name", None),
            "description": result.get("description", "No description available."),
            "hardinessMin": result.get("hardiness_min", "N/A"),
            "hardinessMax": result.get("hardiness_max", "N/A"),
            "bestTemperatureMin": result.get("best_temperature_min", None),
            "bestTemperatureMax": result.get("best_temperature_max", None),
            "requiresGreenhouse": result.get("requires_greenhouse", False),
            "suitableForContainers": result.get("suitable_for_containers", False),
            "growingSeason": result.get("growing_season", "N/A"),
            "waterNeeds": result.get("water_needs", "N/A"),
            "sunlight": result.get("sunlight", "N/A"),
            "spaceRequired": result.get("space_required", "N/A"),
            "sowingMethod": result.get("sowing_method", "N/A"),
            "spread": result.get("spread", None),
            "rowSpacing": result.get("row_spacing", None),
            "height": result.get("height", None),
            "imageUrl": _normalize_image_url(result.get("image_url")),
            "companions": companions
    }

    return jsonify(plant_data)

@plants_bp.route("", methods=["POST"])
def add_plant():
    """Adds a new plant to the database with schema validation."""
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
    
    # Validating using schema
    errors = plant_schema.validate(json_data)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 422
    
    try:
        plant_data = plant_schema.load(json_data)
        new_plant = Plant(**plant_data)
        
        db.session.add(new_plant)
        db.session.commit()
        return jsonify({"message": "Plant added successfully", "id":new_plant.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to add plant: %s", e, exc_info=True)
        return jsonify({"error": "Failed to add plant."}), 500


# -------------------------------------------------------------------
# Care tips data keyed by plant name
# -------------------------------------------------------------------
CARE_TIPS = {
    "Tomato": {
        "growing_tips": [
            "Start seeds indoors 6-8 weeks before the last frost date.",
            "Transplant outdoors when nighttime temperatures stay above 50F (10C).",
            "Plant deep - bury 2/3 of the stem to encourage root growth.",
            "Stake or cage plants early to support heavy fruit.",
            "Prune suckers (the shoots between the main stem and branches) for larger fruit.",
            "Water deeply and consistently - irregular watering causes blossom end rot.",
            "Mulch around the base to retain moisture and prevent soil splash."
        ],
        "common_problems": [
            "Blossom end rot: caused by inconsistent watering and calcium deficiency. Water evenly.",
            "Early blight: brown spots with concentric rings on lower leaves. Remove affected leaves, improve air circulation.",
            "Tomato hornworms: large green caterpillars. Hand-pick or use Bt (Bacillus thuringiensis).",
            "Cracking: caused by heavy rain after a dry spell. Mulch and water consistently.",
            "Blossom drop: flowers fall off without fruiting. Usually caused by extreme heat or cold."
        ],
        "harvesting": "Harvest when fruits are fully colored and slightly soft to the touch. Twist gently or cut from the vine. Green tomatoes can ripen indoors on a sunny windowsill.",
        "storage": "Store ripe tomatoes at room temperature, stem-side down. Never refrigerate - cold damages flavor and texture. Use within a week. Excess tomatoes can be frozen whole, canned, or dried."
    },
    "Cherry Tomato": {
        "growing_tips": [
            "Start seeds indoors 6-8 weeks before last frost.",
            "Very prolific - one plant can produce hundreds of fruits.",
            "Provide sturdy support as vines grow vigorously.",
            "Pinch off suckers for a tidier plant, or let them grow for more fruit.",
            "Water consistently to prevent splitting."
        ],
        "common_problems": [
            "Splitting: caused by sudden increase in water. Water evenly.",
            "Same diseases as regular tomatoes - blight, hornworms, aphids.",
            "Overproduction: harvest regularly to keep plants producing."
        ],
        "harvesting": "Pick when fruits are fully colored and come off the vine easily with a gentle tug. Check daily as they ripen quickly.",
        "storage": "Store at room temperature. Use within a few days for best flavor. Can be frozen, dried, or made into sauce."
    },
    "Basil": {
        "growing_tips": [
            "Start seeds indoors 6 weeks before last frost or direct sow after frost.",
            "Needs warm soil (at least 50F/10C) to germinate well.",
            "Pinch off flower buds as soon as they appear to prolong leaf production.",
            "Harvest from the top down to encourage bushy growth.",
            "Water at the base - wet leaves encourage fungal disease."
        ],
        "common_problems": [
            "Bolting: basil flowers and goes to seed in hot weather. Pinch flowers immediately.",
            "Fusarium wilt: leaves yellow and wilt. Use resistant varieties and rotate crops.",
            "Downy mildew: dark spots on leaves with gray fuzz underneath. Improve air circulation.",
            "Aphids: spray with water or use insecticidal soap."
        ],
        "harvesting": "Harvest leaves regularly, cutting stems just above a leaf pair. This encourages branching. Morning harvest yields the best flavor and oil content.",
        "storage": "Use fresh for best flavor. Store cut stems in water on the counter (not in the fridge). Freeze in olive oil in ice cube trays for long-term storage. Dried basil loses much of its flavor."
    },
    "Pepper": {
        "growing_tips": [
            "Start seeds indoors 8-10 weeks before last frost - peppers are slow starters.",
            "Transplant after soil warms to at least 65F (18C).",
            "Space plants 18-24 inches apart for good air circulation.",
            "Side-dress with compost when first fruits appear.",
            "Some gardeners pick the first few flowers to redirect energy into plant growth."
        ],
        "common_problems": [
            "Blossom drop: flowers fall off in extreme heat (above 90F) or cold (below 55F at night).",
            "Sunscald: white or tan patches on fruit from direct sun. Provide some afternoon shade in hot climates.",
            "Aphids: check undersides of leaves. Use insecticidal soap.",
            "Slow growth early: be patient - peppers grow slowly until soil warms up."
        ],
        "harvesting": "Peppers can be harvested green or left to ripen to their final color (red, yellow, orange) for sweeter flavor. Use pruning shears to avoid damaging the plant.",
        "storage": "Store unwashed in the refrigerator for 1-2 weeks. Freeze chopped peppers for cooking. Dehydrate for pepper flakes."
    },
    "Bell Pepper": {
        "growing_tips": [
            "Start seeds indoors 8-10 weeks before last frost.",
            "Transplant when nighttime temps are consistently above 55F (13C).",
            "Stake plants when fruit starts to form - heavy peppers can topple plants.",
            "Consistent moisture is key - mulch to maintain even soil moisture.",
            "Feed every 2-3 weeks with a balanced fertilizer once fruiting begins."
        ],
        "common_problems": [
            "Blossom end rot: similar to tomatoes, caused by calcium/watering issues.",
            "Slow to ripen: be patient - it takes 2-3 weeks for green peppers to turn color.",
            "Sunscald and aphids are common issues."
        ],
        "harvesting": "Harvest green for a slightly bitter flavor, or wait for full color for sweeter taste. Cut with shears leaving a short stem.",
        "storage": "Refrigerate for up to 2 weeks. Freeze sliced for cooking. Can be roasted and preserved in oil."
    },
    "Hot Pepper": {
        "growing_tips": [
            "Start seeds indoors 8-10 weeks before last frost; hot peppers need extra warmth to germinate.",
            "Use a heat mat for germination - ideal soil temp is 80-85F (27-29C).",
            "Stress can increase heat - slightly reducing water as fruits ripen may boost capsaicin.",
            "Wear gloves when handling very hot varieties."
        ],
        "common_problems": [
            "Same issues as bell peppers: blossom drop in extreme temps, aphids, sunscald.",
            "Cross-pollination: if saving seeds, isolate varieties to prevent crosses."
        ],
        "harvesting": "Harvest when fruits reach their mature color. Wear gloves for very hot varieties. The longer they stay on the vine, the hotter they get.",
        "storage": "Refrigerate for 1-2 weeks. Dry in a dehydrator or string them up to air dry. Freeze whole or make hot sauce."
    },
    "Jalapeno Pepper": {
        "growing_tips": [
            "Start seeds indoors 8-10 weeks before last frost.",
            "Jalapenos are one of the easier hot peppers to grow.",
            "Plants produce heavily - 25-35 peppers per plant is typical.",
            "Cork-like lines (corking) on the skin indicate maturity and more heat."
        ],
        "common_problems": [
            "Blossom drop in extreme heat. Provide afternoon shade if temps exceed 95F.",
            "Aphids and spider mites: use insecticidal soap or neem oil."
        ],
        "harvesting": "Harvest green for milder flavor or wait until they turn red for more heat and sweetness. Corking lines indicate peak ripeness.",
        "storage": "Refrigerate for 1-2 weeks. Smoke and dry for chipotle peppers. Pickle or freeze for long-term storage."
    },
    "Cucumber": {
        "growing_tips": [
            "Direct sow after last frost when soil is at least 60F (16C).",
            "Provide a trellis for vining types to save space and improve air circulation.",
            "Keep soil consistently moist - cucumbers are 95% water.",
            "Mulch heavily to retain moisture and keep fruits clean.",
            "Plant successive crops every 2-3 weeks for continuous harvest."
        ],
        "common_problems": [
            "Powdery mildew: white powder on leaves. Improve air circulation, avoid overhead watering.",
            "Cucumber beetles: yellow-green striped beetles. Use row covers early, hand-pick.",
            "Bitter fruit: caused by heat stress or irregular watering.",
            "Poor pollination: plant flowers nearby to attract bees, or hand-pollinate."
        ],
        "harvesting": "Harvest when fruits are medium-sized and firm. Pick regularly to encourage more production. Do not let cucumbers turn yellow on the vine.",
        "storage": "Wrap in paper towels and refrigerate for up to a week. For pickling, process within 24 hours of harvest. Do not freeze fresh cucumbers."
    },
    "Carrot": {
        "growing_tips": [
            "Direct sow in loose, stone-free soil. Carrots do not transplant well.",
            "Seeds are tiny - mix with sand for even distribution.",
            "Keep soil surface moist until germination (10-21 days).",
            "Thin seedlings to 2-3 inches apart when tops are 2 inches tall.",
            "Grow in raised beds or deep containers if soil is heavy clay."
        ],
        "common_problems": [
            "Forked/deformed roots: caused by rocky or compacted soil. Amend with compost.",
            "Carrot fly: orange-brown tunnels in roots. Use row covers, plant with onions.",
            "Green shoulders: the top of the root turns green from sun exposure. Hill soil around tops.",
            "Slow/poor germination: keep soil consistently moist and be patient."
        ],
        "harvesting": "Harvest when the top of the root is about 3/4 inch diameter. Loosen soil alongside with a fork before pulling. Baby carrots can be harvested earlier.",
        "storage": "Remove tops (they draw moisture from roots). Store unwashed in sand or in perforated bags in the fridge for 2-4 months. Can be frozen after blanching."
    },
    "Lettuce": {
        "growing_tips": [
            "Direct sow in early spring, as soon as soil can be worked.",
            "Successive plantings every 2 weeks ensure continuous harvests.",
            "Prefers cool weather - provide shade in summer to prevent bolting.",
            "Keep soil evenly moist for tender, non-bitter leaves.",
            "Great container plant - grow in window boxes or shallow pots."
        ],
        "common_problems": [
            "Bolting: lettuce flowers and becomes bitter in hot weather. Choose bolt-resistant varieties.",
            "Slugs: use beer traps, diatomaceous earth, or hand-pick at dusk.",
            "Aphids: blast with water or use insecticidal soap.",
            "Tip burn: brown edges caused by calcium deficiency or heat stress."
        ],
        "harvesting": "Harvest outer leaves as needed (cut-and-come-again method), or cut the whole head at the base. Harvest in the morning for crispest leaves.",
        "storage": "Wash, dry thoroughly, and store in the fridge in a container with a paper towel. Use within a week. Lettuce does not freeze well."
    },
    "Romaine Lettuce": {
        "growing_tips": [
            "Direct sow or transplant in cool weather.",
            "More heat-tolerant than other lettuce types but still prefers cool conditions.",
            "Space 8-10 inches apart for full heads.",
            "Provide afternoon shade in warmer climates."
        ],
        "common_problems": [
            "Same issues as regular lettuce: bolting, slugs, aphids.",
            "Heart rot: caused by excess moisture. Ensure good drainage."
        ],
        "harvesting": "Harvest when heads feel firm. Cut at the base or harvest outer leaves over time.",
        "storage": "Refrigerate in a plastic bag with a damp paper towel. Lasts 1-2 weeks."
    },
    "Corn": {
        "growing_tips": [
            "Direct sow after soil reaches 60F (16C). Corn does not transplant well.",
            "Plant in blocks (at least 4 rows) rather than single rows for proper wind pollination.",
            "Space plants 8-12 inches apart in rows 30-36 inches apart.",
            "Corn is a heavy feeder - side-dress with nitrogen when plants are knee-high.",
            "Water deeply during tasseling and silking for full ear development."
        ],
        "common_problems": [
            "Corn earworm: apply a drop of mineral oil to the silk tip after it browns.",
            "Raccoons and birds: use netting or electric fencing.",
            "Poor pollination: small kernels or missing rows. Plant in blocks, not single rows.",
            "Lodging (falling over): hill soil around the base when plants are 12 inches tall."
        ],
        "harvesting": "Harvest when silks are brown and dry, and kernels are plump and release a milky juice when punctured. Usually about 20 days after silks appear.",
        "storage": "Eat within hours for peak sweetness - sugars convert to starch quickly. Refrigerate unhusked for 1-3 days. Blanch and freeze for long-term storage."
    },
    "Potato": {
        "growing_tips": [
            "Plant seed potatoes (not grocery store potatoes) 2-4 weeks before last frost.",
            "Cut seed potatoes into pieces with 2-3 eyes each. Let cuts dry for a day before planting.",
            "Hill soil around plants as they grow - this prevents green potatoes.",
            "Stop watering when foliage begins to yellow and die back.",
            "Do not plant where tomatoes, peppers, or eggplant grew last year."
        ],
        "common_problems": [
            "Green potatoes: exposure to light produces solanine (toxic). Hill soil regularly.",
            "Late blight: same disease that affects tomatoes. Use certified seed, rotate crops.",
            "Colorado potato beetle: hand-pick adults and larvae. Use Bt for larvae.",
            "Scab: rough, corky patches. Keep pH below 5.5, avoid fresh manure."
        ],
        "harvesting": "New potatoes: harvest 2-3 weeks after flowering. Storage potatoes: wait until foliage dies back completely, then wait 2 more weeks before digging.",
        "storage": "Cure in a dark, 45-60F (7-16C) location for 1-2 weeks. Store in a cool, dark, humid place (not the fridge). Properly stored potatoes last 3-6 months."
    },
    "Onion": {
        "growing_tips": [
            "Choose long-day, short-day, or day-neutral varieties based on your latitude.",
            "Start from seeds (10-12 weeks before transplanting), sets, or transplants.",
            "Plant in fertile, well-drained soil with consistent moisture.",
            "Stop watering when tops begin to fall over.",
            "Do not hill soil over the bulb - onions need the top exposed to swell."
        ],
        "common_problems": [
            "Bolting: caused by cold snaps after planting. Choose appropriate varieties.",
            "Onion maggot: lay eggs at the base. Use row covers and rotate crops.",
            "Thrips: tiny insects that cause silver streaking. Blast with water.",
            "Small bulbs: usually caused by planting the wrong day-length variety."
        ],
        "harvesting": "Harvest when 50-80% of tops have fallen over. Pull and cure in a warm, dry, well-ventilated area for 2-4 weeks.",
        "storage": "After curing, store in a cool, dry place in mesh bags or braided. Sweet onions last 1-2 months; storage varieties last 3-6 months."
    },
    "Green Onion": {
        "growing_tips": [
            "Direct sow or plant from sets every 2-3 weeks for continuous harvest.",
            "Can be grown from the root end of grocery store green onions in water.",
            "Very easy to grow in containers or windowsills year-round."
        ],
        "common_problems": [
            "Few problems. Occasional aphids or onion maggots.",
            "Bolting in extreme heat or after vernalization."
        ],
        "harvesting": "Harvest when tops are 6-8 inches tall. Pull the whole plant or cut above the root for regrowth.",
        "storage": "Wrap in a damp paper towel and refrigerate for 1-2 weeks. Stand in water on the counter for a few days."
    },
    "Garlic": {
        "growing_tips": [
            "Plant individual cloves in fall, 6-8 weeks before the ground freezes.",
            "Plant pointed end up, 2 inches deep, 6 inches apart.",
            "Mulch heavily with straw after planting for winter protection.",
            "Remove scapes (flower stalks) in spring to redirect energy to bulb growth.",
            "Stop watering 2-3 weeks before harvest."
        ],
        "common_problems": [
            "Small bulbs: usually from planting too late or not removing scapes.",
            "White rot: a serious fungal disease. Rotate crops and do not replant garlic in the same spot for 5+ years.",
            "Rust: orange spots on leaves. Remove affected leaves, improve air circulation."
        ],
        "harvesting": "Harvest when lower leaves begin to brown but 5-6 green leaves remain (each leaf represents a wrapper layer). Dig carefully to avoid damage.",
        "storage": "Cure in a warm, dry, shaded area with good air flow for 2-4 weeks. Store in a cool, dry place. Hardneck varieties last 3-6 months; softneck lasts 6-9 months."
    },
    "Pea": {
        "growing_tips": [
            "Direct sow in early spring, 4-6 weeks before last frost. Peas love cool weather.",
            "Inoculate seeds with rhizobium bacteria for better nitrogen fixation.",
            "Provide a trellis or support for climbing varieties.",
            "Stop harvesting when plants decline in summer heat.",
            "Plant a fall crop 8-10 weeks before first frost."
        ],
        "common_problems": [
            "Powdery mildew: common in warm, humid weather. Choose resistant varieties.",
            "Aphids: common on peas. Blast with water or use insecticidal soap.",
            "Poor germination in cold, wet soil: wait for soil to reach 45F (7C)."
        ],
        "harvesting": "Shell peas: pick when pods are plump and bright green. Snow peas: pick when pods are flat and tender. Sugar snap peas: pick when pods are plump but before seeds bulge.",
        "storage": "Use immediately for best sweetness. Refrigerate in a bag for 3-5 days. Blanch and freeze for long-term storage."
    },
    "Sugar Snap Pea": {
        "growing_tips": [
            "Same growing needs as regular peas. Provide 5-6 foot trellis.",
            "Very productive - harvest daily once pods start forming.",
            "Succession plant for extended harvest."
        ],
        "common_problems": [
            "Same as regular peas: powdery mildew, aphids.",
            "Tough pods: harvest before peas inside get too large."
        ],
        "harvesting": "Pick when pods are plump and crisp. Eat whole - pod and peas together.",
        "storage": "Refrigerate for 3-5 days. Blanch and freeze for longer storage."
    },
    "Squash": {
        "growing_tips": [
            "Direct sow after last frost when soil is warm (at least 60F/16C).",
            "Summer squash: harvest small and often for best flavor.",
            "Winter squash: let fruits mature fully on the vine until the rind is hard.",
            "Mulch around plants to retain moisture and keep fruit clean.",
            "Hand-pollinate if bee activity is low - use a small brush."
        ],
        "common_problems": [
            "Squash vine borer: wilting plants with sawdust-like frass at the base. Wrap stems with foil.",
            "Powdery mildew: very common on squash. Remove affected leaves, improve air circulation.",
            "Squash bugs: gray-brown flat bugs. Check under leaves for eggs and destroy.",
            "Blossom end rot: similar to tomatoes, caused by inconsistent watering."
        ],
        "harvesting": "Summer squash: harvest at 6-8 inches. Winter squash: wait until the stem is dry and the skin cannot be dented with a fingernail.",
        "storage": "Summer squash: refrigerate for up to a week. Winter squash: cure in a warm place for 2 weeks, then store in a cool, dry location for 3-6 months."
    },
    "Zucchini": {
        "growing_tips": [
            "Direct sow or transplant after last frost.",
            "One or two plants is usually enough for a family - they are very productive.",
            "Harvest regularly to keep plants producing.",
            "Check under large leaves daily - zucchini can grow from small to oversized overnight."
        ],
        "common_problems": [
            "Squash vine borer and powdery mildew are the biggest threats.",
            "Poor pollination: hand-pollinate if needed. Both male and female flowers needed.",
            "Oversized fruit: tough and seedy. Harvest at 6-8 inches."
        ],
        "harvesting": "Harvest when 6-8 inches long for best texture. Cut from the vine with a knife, leaving a short stem.",
        "storage": "Refrigerate for up to a week. Shred and freeze for baking. Can also be dehydrated or pickled."
    },
    "Butternut Squash": {
        "growing_tips": [
            "Start seeds indoors 3-4 weeks before last frost or direct sow after frost.",
            "Needs lots of space - vines can spread 10-15 feet.",
            "Allow fruits to mature fully on the vine for best storage quality."
        ],
        "common_problems": [
            "Same as other squash: vine borers, powdery mildew, squash bugs.",
            "Fruits not ripening: need full sun and warm temperatures."
        ],
        "harvesting": "Harvest when skin is tan and hard, stem is dry, and you cannot dent the skin with your fingernail. Cut with several inches of stem.",
        "storage": "Cure in a warm spot for 2 weeks. Store in a cool (50-55F), dry area for 3-6 months."
    },
    "Winter Squash": {
        "growing_tips": [
            "Direct sow after last frost. Give plants plenty of room.",
            "Slide a piece of cardboard or straw under developing fruits to prevent rot.",
            "Let fruits fully mature on the vine for best storage life."
        ],
        "common_problems": [
            "Same as other squash varieties. Vine borers, powdery mildew.",
            "Fruit rot: keep fruits off wet soil."
        ],
        "harvesting": "Harvest after the first light frost or when the rind is very hard and the stem is dry.",
        "storage": "Cure for 1-2 weeks in a warm place. Store at 50-55F in a dry area. Most varieties last 3-6 months."
    },
    "Pumpkin": {
        "growing_tips": [
            "Direct sow after last frost in hills spaced 6-8 feet apart.",
            "For giant pumpkins, allow only one fruit per vine.",
            "Slide cardboard under developing fruits to prevent bottom rot.",
            "Feed regularly with a high-potassium fertilizer."
        ],
        "common_problems": [
            "Same as squash: vine borers, powdery mildew, squash bugs.",
            "Fruit not setting: poor pollination. Hand-pollinate in early morning."
        ],
        "harvesting": "Harvest when the rind is hard and the stem begins to dry. Leave 4-6 inches of stem attached.",
        "storage": "Cure in a warm, sunny spot for 10 days. Store at 50-55F for 2-3 months."
    },
    "Green Bean": {
        "growing_tips": [
            "Direct sow after last frost when soil is at least 60F (16C).",
            "Bush beans: no support needed, harvest over 2-3 weeks.",
            "Pole beans: provide a trellis, harvest over 6-8 weeks.",
            "Do not over-fertilize with nitrogen - beans fix their own nitrogen.",
            "Succession plant bush beans every 2-3 weeks."
        ],
        "common_problems": [
            "Mexican bean beetle: copper-colored beetles with black spots. Hand-pick.",
            "Rust: reddish-brown spots on leaves. Remove affected plants, rotate crops.",
            "Poor germination: soil too cold or wet. Wait for warm soil.",
            "Bacterial blight: water-soaked spots on leaves. Avoid working in wet plants."
        ],
        "harvesting": "Pick when pods snap cleanly and before seeds bulge. Check daily once harvest begins - regular picking encourages more production.",
        "storage": "Refrigerate unwashed for up to a week. Blanch and freeze for long-term storage. Can also be canned or pickled."
    },
    "Spinach": {
        "growing_tips": [
            "Direct sow in early spring or fall - spinach bolts quickly in heat.",
            "Shade from taller plants helps extend the harvest in warm weather.",
            "Keep soil consistently moist and well-drained.",
            "Succession plant every 2 weeks in cool weather."
        ],
        "common_problems": [
            "Bolting: the primary problem. Grows flower stalk in heat or long days. Choose slow-bolt varieties.",
            "Leaf miners: create tunnels in leaves. Use row covers.",
            "Downy mildew: yellow patches on leaves with gray fuzz underneath."
        ],
        "harvesting": "Harvest outer leaves when they are large enough to eat, or cut the whole plant at the base. Harvest before flower stalk appears.",
        "storage": "Wash, dry thoroughly, and refrigerate in a container with paper towels. Use within a week. Blanch and freeze for long-term storage."
    },
    "Radish": {
        "growing_tips": [
            "Direct sow in early spring or fall. One of the easiest and fastest crops.",
            "Harvest spring radishes in 25-30 days; do not leave too long or they become woody.",
            "Thin to 2 inches apart for round varieties.",
            "Excellent succession crop - sow every 1-2 weeks."
        ],
        "common_problems": [
            "Woody/pithy roots: left in the ground too long or grown in hot weather.",
            "Flea beetles: tiny holes in leaves. Use row covers.",
            "Root maggots: tunnels in roots. Use row covers and rotate crops."
        ],
        "harvesting": "Pull when roots are about 1 inch in diameter (for standard varieties). Do not delay - radishes go from perfect to pithy quickly.",
        "storage": "Remove greens (they draw moisture). Refrigerate in a bag for 1-2 weeks. Winter radishes store much longer."
    },
    "Broccoli": {
        "growing_tips": [
            "Start seeds indoors 6-8 weeks before last frost. Prefers cool weather.",
            "Transplant hardened-off seedlings 2-3 weeks before last frost.",
            "Feed heavily - broccoli is a nutrient-hungry crop.",
            "After cutting the main head, side shoots will produce smaller florets for weeks."
        ],
        "common_problems": [
            "Cabbage worms: green caterpillars eat leaves. Use Bt or row covers.",
            "Bolting: flowers prematurely in heat. Plant early and choose heat-tolerant varieties.",
            "Club root: swollen, distorted roots. Maintain pH above 7.0 in affected areas.",
            "Aphids: check undersides of leaves frequently."
        ],
        "harvesting": "Cut the central head when florets are tight and before any yellow flowers appear. Cut 5-6 inches of stem. Side shoots will continue producing.",
        "storage": "Refrigerate unwashed in a perforated bag for 1-2 weeks. Blanch and freeze for long-term storage."
    },
    "Cabbage": {
        "growing_tips": [
            "Start seeds indoors 6-8 weeks before last frost.",
            "Space 18-24 inches apart for large heads.",
            "Consistent watering prevents head splitting.",
            "Side-dress with nitrogen-rich fertilizer at mid-season."
        ],
        "common_problems": [
            "Cabbage worms and cabbage loopers: use Bt, row covers, or hand-pick.",
            "Splitting: caused by overwatering or heavy rain after dry period.",
            "Club root: keep soil pH above 7.0.",
            "Aphids: common on brassicas."
        ],
        "harvesting": "Harvest when heads are firm and solid. Cut at the base. Leave the outer leaves and stem - a second smaller head may grow.",
        "storage": "Refrigerate whole heads for 1-2 months. Can be fermented into sauerkraut for long-term storage."
    },
    "Cauliflower": {
        "growing_tips": [
            "The trickiest brassica to grow - very sensitive to temperature fluctuations.",
            "Start seeds indoors 6-8 weeks before last frost.",
            "Blanch white varieties by tying outer leaves over the developing head.",
            "Keep soil consistently moist and feed regularly."
        ],
        "common_problems": [
            "Buttoning: forms tiny heads instead of full ones. Caused by stress (heat, cold, drought).",
            "Same pests as other brassicas: cabbage worms, aphids, flea beetles.",
            "Discolored heads: caused by sun exposure. Blanch heads by tying leaves."
        ],
        "harvesting": "Harvest when heads are 6-8 inches across, white, and compact. Do not wait for them to separate.",
        "storage": "Refrigerate in a plastic bag for 1-2 weeks. Blanch and freeze, or pickle for longer storage."
    },
    "Kale": {
        "growing_tips": [
            "Direct sow or transplant in spring or late summer for fall harvest.",
            "One of the hardiest greens - survives frost, which actually improves flavor.",
            "Harvest outer leaves regularly to promote new growth.",
            "Can produce well into winter with minimal protection."
        ],
        "common_problems": [
            "Cabbage worms: same as other brassicas. Use Bt or row covers.",
            "Aphids: can be heavy on kale. Blast with water.",
            "Whiteflies: yellow sticky traps help control populations."
        ],
        "harvesting": "Harvest outer leaves when they reach about 8-10 inches long. Leave the central growing point intact for continued production.",
        "storage": "Refrigerate in a bag for 1-2 weeks. Massage and freeze for smoothies. Dehydrate for kale chips."
    },
    "Brussels Sprouts": {
        "growing_tips": [
            "Start seeds indoors 12-14 weeks before first frost. They need a long, cool growing season.",
            "Space 24-30 inches apart.",
            "Remove lower leaves as sprouts develop to improve air circulation.",
            "Topping the plant (removing the growing tip) 3-4 weeks before harvest encourages uniform sprout development."
        ],
        "common_problems": [
            "Same brassica pests: cabbage worms, aphids.",
            "Loose sprouts: caused by too much heat or nitrogen. Plant for fall harvest.",
            "Very long growing season required - not suitable for areas with short, warm seasons."
        ],
        "harvesting": "Harvest from the bottom up when sprouts are 1-2 inches in diameter and firm. Twist or cut from the stalk. Frost improves flavor.",
        "storage": "Refrigerate on the stalk for up to 3 weeks, or remove and refrigerate for 1 week. Blanch and freeze."
    },
    "Eggplant": {
        "growing_tips": [
            "Start seeds indoors 8-10 weeks before last frost. Needs warmth to thrive.",
            "Do not transplant until soil is at least 60F (16C) and nights are above 55F.",
            "Stake plants to support heavy fruit.",
            "Mulch to retain warmth and moisture."
        ],
        "common_problems": [
            "Flea beetles: tiny holes in leaves. Use row covers on young plants.",
            "Verticillium wilt: plants wilt despite adequate water. Rotate crops.",
            "Colorado potato beetle: also attacks eggplant. Hand-pick."
        ],
        "harvesting": "Harvest when skin is glossy and firm, and flesh springs back when pressed. Dull skin means overripe. Cut with shears leaving 1 inch of stem.",
        "storage": "Use within a few days for best quality. Refrigerate for up to a week. Can be frozen (cooked first), grilled, or pickled."
    },
    "Strawberry": {
        "growing_tips": [
            "Plant in spring as soon as soil can be worked.",
            "June-bearing: one large harvest. Everbearing: harvests spring through fall.",
            "Remove runners in the first year to establish strong plants.",
            "Renovate June-bearing beds after harvest by mowing, thinning, and fertilizing.",
            "Mulch with straw to keep fruit clean and protect roots in winter."
        ],
        "common_problems": [
            "Birds: use netting to protect ripening fruit.",
            "Slugs: use beer traps or diatomaceous earth.",
            "Gray mold (botrytis): fuzzy gray mold on fruit. Improve air circulation, remove affected fruit.",
            "Runners: can take over. Remove excess runners to maintain productivity."
        ],
        "harvesting": "Pick when fruits are fully red with no white shoulders. Harvest in the morning for best flavor. Pick every 2-3 days.",
        "storage": "Refrigerate unwashed for 3-5 days. Freeze on a sheet pan then transfer to bags. Excellent for jam and preserves."
    },
    "Blueberry": {
        "growing_tips": [
            "Plant in very acidic soil (pH 4.5-5.5). Amend with sulfur and peat moss.",
            "Plant at least 2 varieties for cross-pollination and better yields.",
            "Mulch with pine needles or acidic wood chips.",
            "Prune in late winter - remove dead wood and oldest canes.",
            "Patience: bushes take 3-5 years to reach full production."
        ],
        "common_problems": [
            "Birds: the biggest problem. Use netting.",
            "Iron chlorosis: yellow leaves with green veins. Soil pH is too high.",
            "Mummy berry: shriveled fruit. Remove fallen berries, prune for air flow."
        ],
        "harvesting": "Berries are ripe 2-3 days after they turn fully blue. They should come off easily with a gentle tug. Not all berries ripen at once.",
        "storage": "Refrigerate unwashed for 1-2 weeks. Freeze on a sheet pan then bag. Excellent for jams, pies, and drying."
    },
    "Raspberry": {
        "growing_tips": [
            "Plant bare-root canes in early spring. Space 2-3 feet apart in rows.",
            "Summer-bearing: fruit on second-year canes. Ever-bearing: fruit on first-year canes.",
            "Provide a trellis or wire support system.",
            "Prune spent canes (brown ones) after harvest."
        ],
        "common_problems": [
            "Raspberry cane borer: canes wilt from the top. Cut below the wilted section.",
            "Japanese beetles: hand-pick or use traps away from plants.",
            "Viruses: buy certified disease-free stock. Remove and destroy infected plants."
        ],
        "harvesting": "Berries are ripe when they pull easily from the plant with the core staying on the plant. Harvest every 2-3 days.",
        "storage": "Very perishable - refrigerate and use within 2-3 days. Freeze in a single layer. Excellent for jam."
    },
    "Blackberry": {
        "growing_tips": [
            "Plant in spring. Choose thornless varieties for easier management.",
            "Provide a strong trellis - canes can grow 6-10 feet.",
            "Tip-prune first-year canes at 3-4 feet to encourage branching.",
            "Mulch heavily to suppress weeds and retain moisture."
        ],
        "common_problems": [
            "Orange rust: bright orange pustules on leaves. Remove and destroy infected plants.",
            "Spotted wing drosophila: fruit fly that lays eggs in ripening fruit. Use fine mesh netting.",
            "Aggressive spreading: contain with root barriers or regular sucker removal."
        ],
        "harvesting": "Pick when berries are fully black, plump, and come off easily. Taste one - they should be sweet, not tart.",
        "storage": "Very perishable. Refrigerate and use within 2-3 days. Freeze in a single layer on a sheet pan."
    },
    "Asparagus": {
        "growing_tips": [
            "Plant crowns in spring in a trench 12 inches deep, spaced 18 inches apart.",
            "Do NOT harvest the first 2 years - let plants establish strong root systems.",
            "Mulch heavily and keep weeds controlled.",
            "Leave fern-like foliage standing until it dies back in winter."
        ],
        "common_problems": [
            "Asparagus beetle: feed on spears and fern. Hand-pick or use neem oil.",
            "Fusarium wilt: yellowing ferns. Plant resistant varieties.",
            "Crown rot: caused by poor drainage. Ensure well-drained soil."
        ],
        "harvesting": "In year 3+, harvest spears when they are 6-8 inches tall and pencil-thick. Snap at ground level. Harvest for 6-8 weeks, then let remaining spears grow into ferns.",
        "storage": "Stand spears upright in 1 inch of water in the fridge for up to a week. Blanch and freeze for long-term storage. Can also be pickled."
    },
    "Herb": {
        "growing_tips": [
            "Most herbs prefer well-drained soil and full sun.",
            "Harvest regularly to encourage bushy growth.",
            "Pinch off flower buds to prolong leaf production."
        ],
        "common_problems": [
            "Root rot: caused by overwatering. Herbs prefer slightly dry conditions.",
            "Bolting in heat: harvest frequently and provide afternoon shade."
        ],
        "harvesting": "Harvest in the morning after dew dries for peak essential oil content.",
        "storage": "Dry by hanging bundles upside down in a warm, dark place. Store dried herbs in airtight containers."
    },
    "Cilantro": {
        "growing_tips": [
            "Direct sow in cool weather. Cilantro bolts quickly in heat.",
            "Succession plant every 2-3 weeks for continuous harvest.",
            "Let some plants go to seed for coriander, a different spice from the same plant.",
            "Partial shade helps delay bolting in warm climates."
        ],
        "common_problems": [
            "Bolting: the main challenge. Plant slow-bolt varieties like 'Calypso' or 'Santo'.",
            "Leaf spot: brown spots on leaves. Improve air circulation."
        ],
        "harvesting": "Cut leaves when plants are 6 inches tall. For coriander seeds, let plants flower and collect dried seeds.",
        "storage": "Store stems in water on the counter or refrigerate in a jar of water covered with a plastic bag. Freeze in olive oil. Dried cilantro has little flavor."
    },
    "Dill": {
        "growing_tips": [
            "Direct sow after last frost. Dill has a taproot and does not transplant well.",
            "Succession plant every 3 weeks for continuous harvest.",
            "Will self-seed readily if allowed to flower."
        ],
        "common_problems": [
            "Bolting: dill flowers quickly in heat. Harvest frequently.",
            "Swallowtail caterpillars: eat foliage. Consider leaving some for the butterflies."
        ],
        "harvesting": "Snip leaves as needed. For dill seed, let flower heads dry on the plant, then cut and shake into a bag.",
        "storage": "Freeze fresh dill in bags - it retains more flavor than drying. Dill seeds store well in airtight containers."
    },
    "Parsley": {
        "growing_tips": [
            "Slow to germinate (2-4 weeks). Soak seeds overnight to speed germination.",
            "Start indoors 8-10 weeks before last frost or direct sow in spring.",
            "Biennial - produces leaves the first year, flowers the second.",
            "Harvest outer stems first to promote new growth."
        ],
        "common_problems": [
            "Slow germination: be patient. Keep soil moist.",
            "Swallowtail caterpillars: same as dill. Consider sharing with butterflies.",
            "Crown rot in wet conditions."
        ],
        "harvesting": "Cut outer stems at the base when plants have at least 3 segments of leaves. Regular harvesting encourages bushy growth.",
        "storage": "Refrigerate stems in water or wrap in damp paper towels. Freeze in oil or water for cooking. Dries well too."
    },
    "Rosemary": {
        "growing_tips": [
            "Start from cuttings or nursery plants - seeds are slow and unreliable.",
            "Needs excellent drainage. Add sand or gravel to heavy soils.",
            "Drought-tolerant once established - do not overwater.",
            "Bring indoors in zones below 7 for winter."
        ],
        "common_problems": [
            "Root rot: the biggest killer. Never let roots sit in water.",
            "Powdery mildew: improve air circulation.",
            "Spider mites indoors: mist occasionally and ensure good air flow."
        ],
        "harvesting": "Snip sprigs as needed. Do not remove more than one-third of the plant at a time. Harvest in the morning for peak oil content.",
        "storage": "Fresh sprigs last 1-2 weeks in the fridge wrapped in a damp paper towel. Dries beautifully - hang bundles upside down. Freeze whole sprigs."
    },
    "Sage": {
        "growing_tips": [
            "Start from nursery plants or cuttings. Full sun and well-drained soil.",
            "Prune in early spring to prevent woody, leggy growth.",
            "Replace plants every 3-5 years as they become less productive."
        ],
        "common_problems": [
            "Powdery mildew: improve air circulation.",
            "Root rot: do not overwater.",
            "Becomes woody with age: prune regularly."
        ],
        "harvesting": "Harvest leaves before flowering for best flavor. Do not harvest heavily in the first year.",
        "storage": "Dries exceptionally well. Hang bundles upside down or use a dehydrator. Store dried sage in airtight jars."
    },
    "Thyme": {
        "growing_tips": [
            "Start from nursery plants or divisions. Plant in well-drained, slightly alkaline soil.",
            "Very drought-tolerant once established.",
            "Trim after flowering to keep plants compact.",
            "Excellent ground cover and container plant."
        ],
        "common_problems": [
            "Root rot: needs excellent drainage.",
            "Becomes woody over time: divide plants every 3-4 years."
        ],
        "harvesting": "Snip sprigs as needed. Harvest just before flowers open for peak flavor.",
        "storage": "Dries very well - one of the few herbs that may be more flavorful dried. Store in airtight containers."
    },
    "Oregano": {
        "growing_tips": [
            "Start from nursery plants for best flavor (seeds produce variable results).",
            "Full sun and well-drained soil. Thrives in poor soil.",
            "Cut back to the ground in early spring for fresh new growth.",
            "Spreads via underground runners - contain if needed."
        ],
        "common_problems": [
            "Root rot: do not overwater.",
            "Aphids: blast with water.",
            "Can become invasive: divide regularly."
        ],
        "harvesting": "Harvest stems just before flowers open for peak flavor. Cut stems, leaving at least 2 inches of growth.",
        "storage": "Dries exceptionally well and flavor intensifies. Hang bundles or use a dehydrator."
    },
    "Mint": {
        "growing_tips": [
            "ALWAYS grow in containers - mint is extremely invasive.",
            "Thrives in partial shade and moist soil.",
            "Cut back to the ground in late fall. It will return vigorously in spring.",
            "Take cuttings easily in water."
        ],
        "common_problems": [
            "Invasiveness: the main issue. Containerize!",
            "Rust: orange spots on leaves. Remove affected stems.",
            "Mint flea beetle: small holes in leaves."
        ],
        "harvesting": "Harvest sprigs as needed. Cut stems just above a leaf pair. Frequent harvesting promotes bushier growth.",
        "storage": "Refrigerate stems in water for about a week. Freeze in ice cube trays with water. Dries well but loses some aroma."
    },
    "Peppermint": {
        "growing_tips": [
            "Grow in containers to prevent aggressive spreading.",
            "Prefers partial shade and moist soil.",
            "Cut back hard in late fall. Returns vigorously in spring."
        ],
        "common_problems": [
            "Same as mint: extremely invasive if not contained.",
            "Rust: remove affected leaves."
        ],
        "harvesting": "Harvest just before flowering for peak menthol content. Cut stems in the morning.",
        "storage": "Dry by hanging bundles. Store leaves in airtight containers. Makes excellent tea."
    },
    "Chives": {
        "growing_tips": [
            "Very easy to grow from seeds or divisions. Full sun to partial shade.",
            "Divide clumps every 3-4 years to maintain vigor.",
            "Flowers are edible and attract pollinators.",
            "One of the first herbs to emerge in spring."
        ],
        "common_problems": [
            "Few problems. Occasionally onion thrips.",
            "Can self-seed aggressively: remove flowers if you do not want volunteers."
        ],
        "harvesting": "Cut leaves 2 inches above the base with scissors. New growth appears in 2-3 weeks.",
        "storage": "Refrigerate for about a week. Freeze chopped chives - they maintain flavor better than drying."
    },
    "Lavender": {
        "growing_tips": [
            "Plant in full sun with excellent drainage. Amend heavy soil with gravel.",
            "Do not over-fertilize - lean soil produces more fragrant plants.",
            "Prune in early spring, cutting back by one-third. Never cut into old wood.",
            "English lavender is hardiest; French/Spanish types need warmer climates."
        ],
        "common_problems": [
            "Root rot: the biggest killer. Needs perfect drainage.",
            "Shab disease: causes branches to die back. Remove affected branches.",
            "Winter kill: mulch crown lightly in cold climates."
        ],
        "harvesting": "Cut flower stems when about half the buds have opened. Harvest in the morning after dew dries.",
        "storage": "Hang bundles upside down to dry. Store dried lavender in airtight containers. Retains fragrance for years."
    },
    "Sunflower": {
        "growing_tips": [
            "Direct sow after last frost. Seeds germinate in 7-10 days.",
            "Tall varieties need staking in windy areas.",
            "For continuous blooms, succession plant every 2-3 weeks.",
            "Most varieties are one stem, one flower. Branching types produce multiple blooms."
        ],
        "common_problems": [
            "Birds eating seeds: cover heads with netting or paper bags.",
            "Downy mildew: avoid overhead watering.",
            "Stem weevils: can cause stems to break. Stake tall varieties."
        ],
        "harvesting": "For seeds: harvest when the back of the head turns brown and seeds are plump. For cut flowers: cut when petals start to open.",
        "storage": "Dry seed heads in a warm, dry place. Shell seeds and store in airtight containers. Roast for eating."
    },
    "Sweet Potato": {
        "growing_tips": [
            "Plant slips (rooted sprouts) after soil reaches 65F (18C).",
            "Grow your own slips from a store-bought sweet potato in water.",
            "Black plastic mulch warms soil and improves yields.",
            "Vines spread 10+ feet - give them room or grow bush varieties."
        ],
        "common_problems": [
            "Wireworms and voles: common in new garden beds. Grow in raised beds.",
            "Sweet potato weevil: in southern regions. Rotate crops.",
            "Cracking: caused by irregular watering."
        ],
        "harvesting": "Harvest before first frost. Dig carefully to avoid cuts. Handle gently - sweet potatoes bruise easily.",
        "storage": "Cure at 80-85F and high humidity for 7-10 days. Then store at 55-60F for 6-12 months. Do not refrigerate."
    },
    "Swiss Chard": {
        "growing_tips": [
            "Direct sow in spring or fall. Tolerates both heat and light frost.",
            "One of the most heat-tolerant greens.",
            "Harvest outer leaves to keep plants producing all season.",
            "Beautiful enough for ornamental beds with its colorful stems."
        ],
        "common_problems": [
            "Leaf miners: create tunnels in leaves. Remove affected leaves, use row covers.",
            "Slugs in wet conditions. Use beer traps.",
            "Cercospora leaf spot: tan spots with purple borders. Improve air circulation."
        ],
        "harvesting": "Cut outer stalks at the base when they reach 8-12 inches. New leaves will continue growing from the center.",
        "storage": "Refrigerate in a bag for about a week. Blanch and freeze for longer storage."
    },
    "Beet": {
        "growing_tips": [
            "Direct sow in cool weather, 2-4 weeks before last frost.",
            "Each beet 'seed' is actually a cluster - thin to 3-4 inches apart.",
            "Harvest both roots and greens - beet greens are delicious and nutritious.",
            "Succession plant every 3 weeks for continuous harvest."
        ],
        "common_problems": [
            "Woody roots: left in the ground too long. Harvest at 1.5-3 inches diameter.",
            "Leaf miners: tunnels in leaves. Remove affected leaves.",
            "Poor germination: soak seeds overnight before planting."
        ],
        "harvesting": "Pull when roots are 1.5-3 inches across. Larger beets tend to be woody. Greens can be harvested earlier.",
        "storage": "Remove tops (leave 1 inch of stem). Store unwashed in the fridge for 2-3 months. Can be pickled, roasted, or frozen."
    },
    "Okra": {
        "growing_tips": [
            "Direct sow when soil reaches 65F (18C). Soak seeds overnight for faster germination.",
            "Loves heat - the hotter the better.",
            "Plants grow 4-6 feet tall. Space 12-18 inches apart.",
            "Harvest daily once pods start forming."
        ],
        "common_problems": [
            "Slow germination: soak seeds and ensure warm soil.",
            "Stinkbugs: hand-pick. Can cause misshapen pods.",
            "Root-knot nematodes: rotate crops."
        ],
        "harvesting": "Harvest pods when 2-4 inches long and still tender. Use a knife or shears - stems are tough. Wear gloves if pods are prickly.",
        "storage": "Refrigerate for 2-3 days. Blanch and freeze, pickle, or dehydrate for longer storage."
    },
    "Watermelon": {
        "growing_tips": [
            "Start seeds indoors 3-4 weeks before last frost, or direct sow after soil is 70F (21C).",
            "Needs lots of space - vines spread 10+ feet.",
            "Reduce watering as fruits approach maturity for sweeter flavor.",
            "Slide cardboard under developing melons to prevent bottom rot."
        ],
        "common_problems": [
            "Poor pollination: plant flowers nearby to attract bees.",
            "Anthracnose: dark spots on leaves and fruit. Rotate crops, avoid overhead watering.",
            "Fusarium wilt: plants wilt and die. Plant resistant varieties."
        ],
        "harvesting": "Check for ripeness: the tendril nearest the fruit turns brown, the bottom turns yellow, and the melon sounds hollow when thumped.",
        "storage": "Whole watermelons last 1-2 weeks at room temperature. Cut melon should be refrigerated and used within 5 days."
    },
    "Cantaloupe": {
        "growing_tips": [
            "Start seeds indoors or direct sow after last frost in warm soil.",
            "Needs full sun and warm temperatures to develop sugar.",
            "Black plastic mulch helps warm soil.",
            "Reduce watering in the last week before harvest for sweeter fruit."
        ],
        "common_problems": [
            "Same as other cucurbits: powdery mildew, cucumber beetles.",
            "Poor flavor: not enough sun or harvested too early."
        ],
        "harvesting": "Ripe cantaloupes 'slip' from the vine with gentle pressure. The stem end will smell sweet. Skin changes from green to tan.",
        "storage": "Ripen on the counter. Once ripe, refrigerate for up to 5 days. Cut melon should be refrigerated."
    },
    "Leek": {
        "growing_tips": [
            "Start seeds indoors 10-12 weeks before last frost.",
            "Transplant into deep holes or trenches and fill in gradually to blanch the stem.",
            "Very cold-hardy - can overwinter in many climates.",
            "Hill soil around stems as they grow for longer white portions."
        ],
        "common_problems": [
            "Onion maggot and thrips: similar to onions.",
            "Rust: orange pustules on leaves. Remove affected leaves.",
            "Bolting in second year: harvest before flower stalk forms."
        ],
        "harvesting": "Harvest from fall through early spring. Dig alongside the leek and pull gently to keep the stem intact.",
        "storage": "Refrigerate unwashed for 2-3 weeks. Can be frozen sliced. Leave in the ground and harvest as needed in winter."
    },
    "Celery": {
        "growing_tips": [
            "Start seeds indoors 10-12 weeks before last frost. Very slow germinator.",
            "Needs consistently moist, fertile soil.",
            "Blanch stalks by hilling soil or wrapping in paper for milder flavor.",
            "Heavy feeder - apply compost tea every 2 weeks."
        ],
        "common_problems": [
            "Bolting: caused by cold exposure after transplanting. Harden off gradually.",
            "Leaf blight: brown spots on leaves. Remove affected foliage.",
            "Hollow stalks: caused by boron deficiency."
        ],
        "harvesting": "Harvest individual outer stalks as needed, or cut the whole plant at the base. Stalks should be crisp and about 8 inches long.",
        "storage": "Wrap in foil and refrigerate for 2-4 weeks. Freeze chopped for soups. Celery loses crunch when frozen."
    },
    "Artichoke": {
        "growing_tips": [
            "Start seeds indoors 8-10 weeks before last frost. Can also grow from root divisions.",
            "Perennial in zones 7-11. Treat as an annual in colder zones with vernalization.",
            "Plants are large (4-5 feet) - give them space.",
            "In cold climates, vernalize seedlings by exposing to cool temperatures (below 50F) for 2 weeks."
        ],
        "common_problems": [
            "Aphids: very common on artichokes. Blast with water or use ladybugs.",
            "Slugs and snails: use traps or barriers.",
            "Crown rot in wet, poorly drained soil."
        ],
        "harvesting": "Cut buds before they begin to open, when they are still tight and compact. The central bud matures first. Cut with 3 inches of stem.",
        "storage": "Refrigerate in a plastic bag for 1-2 weeks. Can be marinated, frozen, or canned."
    },
    "Arugula": {
        "growing_tips": [
            "Direct sow in cool weather. One of the easiest greens to grow.",
            "Succession plant every 2-3 weeks for continuous harvest.",
            "Bolts quickly in heat - grow in spring and fall.",
            "Partial shade extends the harvest in warm weather."
        ],
        "common_problems": [
            "Bolting: the main challenge. Plant bolt-resistant varieties.",
            "Flea beetles: tiny holes in leaves. Use row covers."
        ],
        "harvesting": "Harvest young leaves at 2-3 inches for salads. Older leaves are spicier. Cut-and-come-again method works well.",
        "storage": "Refrigerate in a bag with a paper towel for 3-5 days. Does not freeze well."
    },
    "Bok Choy": {
        "growing_tips": [
            "Direct sow in early spring or late summer. Prefers cool weather.",
            "Space baby varieties 6 inches apart, full-size 10-12 inches.",
            "Keep soil consistently moist.",
            "Grow baby bok choy in containers for quick harvests."
        ],
        "common_problems": [
            "Bolting in heat: grow as a spring or fall crop.",
            "Flea beetles and cabbage worms: use row covers.",
            "Slugs in wet weather."
        ],
        "harvesting": "Baby bok choy: harvest whole plant at 6-8 inches. Full-size: harvest outer leaves or cut the whole plant at the base.",
        "storage": "Refrigerate unwashed for about a week. Stir-fry and freeze for longer storage."
    },
    "Turnip": {
        "growing_tips": [
            "Direct sow in spring or fall. Very fast growing (45-60 days).",
            "Thin to 4-6 inches apart for root production.",
            "Both roots and greens are edible.",
            "Tolerates light frost - flavor improves after cold weather."
        ],
        "common_problems": [
            "Root maggots: use row covers.",
            "Flea beetles: tiny holes in leaves.",
            "Woody roots: harvest when 2-3 inches across."
        ],
        "harvesting": "Pull roots when 2-3 inches in diameter. Greens can be harvested earlier.",
        "storage": "Remove tops and refrigerate roots for 2-3 weeks. Greens wilt quickly - use within a few days."
    },
    "Rhubarb": {
        "growing_tips": [
            "Plant crowns in early spring. Perennial that lasts 10-15 years.",
            "Do NOT harvest for the first two years.",
            "Remove flower stalks immediately to redirect energy to stalks.",
            "NEVER eat the leaves - they contain toxic oxalic acid."
        ],
        "common_problems": [
            "Crown rot: needs well-drained soil.",
            "Slugs: use barriers or traps.",
            "Thin stalks: divide plants every 5-8 years."
        ],
        "harvesting": "Pull (do not cut) stalks when they are 12-18 inches long. Take no more than half the stalks at once. Stop harvesting by late June.",
        "storage": "Refrigerate for 1-2 weeks. Chop and freeze for pies and sauces. Makes excellent jam."
    },
    "Fig": {
        "growing_tips": [
            "Plant in a sheltered, south-facing location in cooler climates.",
            "Container growing allows moving indoors for winter in cold zones.",
            "Figs fruit on both old and new wood, depending on variety.",
            "Water deeply but infrequently once established."
        ],
        "common_problems": [
            "Winter kill in cold climates: wrap trees or grow in pots.",
            "Birds and squirrels: use netting.",
            "Root-knot nematodes: grow in containers if this is a problem."
        ],
        "harvesting": "Harvest when figs are soft, drooping, and have a slight crack near the stem. They should pull off easily. Figs do not ripen off the tree.",
        "storage": "Very perishable - eat within 2-3 days. Refrigerate for up to a week. Excellent dried, preserved, or made into jam."
    },
    "Grape": {
        "growing_tips": [
            "Plant in spring in full sun with good air circulation.",
            "Provide a sturdy trellis system. Grapes need annual pruning.",
            "Prune heavily in late winter while dormant.",
            "Takes 3 years to produce a significant crop."
        ],
        "common_problems": [
            "Powdery mildew and downy mildew: good air circulation is essential.",
            "Japanese beetles: hand-pick or use traps.",
            "Birds: netting is necessary as fruit ripens."
        ],
        "harvesting": "Grapes do not ripen off the vine. Taste-test for sweetness. Cut whole clusters with shears.",
        "storage": "Refrigerate unwashed in a bag for 1-2 weeks. Freeze for smoothies. Make juice, wine, or jam."
    },
    "Collard Greens": {
        "growing_tips": [
            "Direct sow or transplant in spring or late summer.",
            "Extremely cold-hardy - flavor improves after frost.",
            "Harvest outer leaves for a long harvest season.",
            "Can produce well into winter, even in snow."
        ],
        "common_problems": [
            "Same brassica pests: cabbage worms, aphids, flea beetles.",
            "Bolting in extended heat."
        ],
        "harvesting": "Harvest lower leaves when they are large and dark green. Leave the growing tip intact.",
        "storage": "Refrigerate for about a week. Blanch and freeze for months of storage."
    },
    "Endive": {
        "growing_tips": [
            "Direct sow in spring or late summer for fall harvest.",
            "Blanch by tying outer leaves over the center 2-3 weeks before harvest for milder flavor.",
            "Prefers cool weather."
        ],
        "common_problems": [
            "Bolting in heat. Grow as spring or fall crop.",
            "Slugs and aphids."
        ],
        "harvesting": "Harvest the whole head when it is full and crisp. Or harvest outer leaves.",
        "storage": "Refrigerate for 1-2 weeks."
    },
    "Kohlrabi": {
        "growing_tips": [
            "Direct sow in spring or fall. Quick growing (45-60 days).",
            "Harvest when bulbs are 2-3 inches across for best tenderness.",
            "Both the bulb and young leaves are edible."
        ],
        "common_problems": [
            "Same as brassicas: cabbage worms, aphids.",
            "Woody texture if left too long or grown in heat."
        ],
        "harvesting": "Harvest when bulbs are 2-3 inches across. Larger bulbs become tough and woody.",
        "storage": "Remove leaves and refrigerate bulbs for 2-3 weeks."
    },
    "Fennel": {
        "growing_tips": [
            "Direct sow in late summer for a fall crop. Bolts in spring plantings.",
            "Grow fennel away from other plants - it is allelopathic (inhibits nearby plants).",
            "Hill soil around the base to blanch the bulb."
        ],
        "common_problems": [
            "Bolting: very prone in spring. Plant in late summer.",
            "Swallowtail caterpillars: same as dill. Share with butterflies."
        ],
        "harvesting": "Harvest bulb when it is 3-4 inches across. Cut at soil level. Fronds can be snipped anytime.",
        "storage": "Refrigerate bulbs for 1-2 weeks. Fronds wilt quickly - use within days. Can be frozen or pickled."
    },
    "Marigold": {
        "growing_tips": [
            "Direct sow after last frost or start indoors 6-8 weeks early.",
            "Deadhead spent blooms to encourage continuous flowering.",
            "Plant throughout the vegetable garden as a pest deterrent.",
            "French marigolds repel nematodes better than other types."
        ],
        "common_problems": [
            "Spider mites in hot, dry weather. Spray with water.",
            "Powdery mildew: improve air circulation.",
            "Slugs on young plants."
        ],
        "harvesting": "Cut flowers as they open for bouquets. Deadhead regularly.",
        "storage": "Dry seed heads at end of season. Save seeds for next year."
    },
    "Nasturtium": {
        "growing_tips": [
            "Direct sow after last frost. Very easy to grow.",
            "Prefers poor soil - too much fertility produces leaves instead of flowers.",
            "Trailing types work well in hanging baskets.",
            "All parts are edible - flowers, leaves, and seed pods."
        ],
        "common_problems": [
            "Aphids: nasturtiums attract aphids (use as a trap crop).",
            "Cabbage white butterflies: also attracted to nasturtiums."
        ],
        "harvesting": "Pick flowers, leaves, and green seed pods as desired. Flowers add peppery flavor to salads.",
        "storage": "Use fresh. Flowers do not store well. Pickle green seed pods as 'poor man's capers'."
    },
    "Borage": {
        "growing_tips": [
            "Direct sow after last frost. Self-seeds readily.",
            "Attracts bees and beneficial insects with its star-shaped blue flowers.",
            "Grows 2-3 feet tall. Plant in back of beds."
        ],
        "common_problems": [
            "Few pest problems. Can become weedy from self-seeding.",
            "Remove unwanted seedlings in spring."
        ],
        "harvesting": "Pick young leaves and flowers as needed. Flowers are edible and beautiful in salads or frozen in ice cubes.",
        "storage": "Use fresh. Does not dry or freeze well. Flowers can be frozen in ice cubes."
    },
    "Ginger": {
        "growing_tips": [
            "Plant fresh rhizome pieces indoors in early spring.",
            "Needs warm, humid conditions - grow as a houseplant in cool climates.",
            "Takes 8-10 months to mature.",
            "Partial shade and rich, moist soil."
        ],
        "common_problems": [
            "Root rot: do not overwater. Needs good drainage.",
            "Slow growth in cool temperatures."
        ],
        "harvesting": "Harvest entire plant after foliage dies back (8-10 months). For young ginger, harvest after 4-5 months.",
        "storage": "Refrigerate unpeeled in a bag for 2-3 weeks. Freeze for months. Can also be dried or pickled."
    },
    "Turmeric": {
        "growing_tips": [
            "Similar to ginger - plant rhizomes indoors in spring.",
            "Needs warm temperatures and high humidity.",
            "Takes 8-10 months to mature.",
            "Beautiful tropical foliage."
        ],
        "common_problems": [
            "Root rot from overwatering.",
            "Spider mites in dry indoor conditions."
        ],
        "harvesting": "Harvest when foliage dies back in fall. Dig up the whole plant and separate rhizomes.",
        "storage": "Fresh turmeric keeps 2-3 weeks in the fridge. Freeze for months. Can be dried and ground."
    },
    "Sunchoke": {
        "growing_tips": [
            "Plant tubers in spring, 4-6 inches deep.",
            "Plants grow 6-10 feet tall - use as a windbreak or privacy screen.",
            "Extremely easy to grow and spreads aggressively.",
            "Harvest in fall after frost kills the tops."
        ],
        "common_problems": [
            "Invasiveness: very hard to eradicate once established. Plant in contained areas.",
            "Sclerotinia rot: white mold at the base. Improve air circulation."
        ],
        "harvesting": "Dig tubers after first frost. Leave some in the ground for next year's crop. Flavor improves after frost.",
        "storage": "Refrigerate in a bag for 2-3 weeks. Leave in the ground and harvest as needed through winter."
    },
    "Lemongrass": {
        "growing_tips": [
            "Start from grocery store stalks rooted in water.",
            "Needs full sun and regular water. Frost-sensitive.",
            "Grow in containers in cold climates and bring indoors in winter.",
            "Divide clumps every 2-3 years."
        ],
        "common_problems": [
            "Frost damage: bring indoors before first frost.",
            "Rust: remove affected leaves."
        ],
        "harvesting": "Cut stalks at the base when they are at least 1/2 inch thick. Use the white lower portion.",
        "storage": "Refrigerate stalks for 2-3 weeks. Freeze whole stalks. Dry outer leaves for tea."
    },
    "Stevia": {
        "growing_tips": [
            "Start from nursery plants. Grow as an annual in most climates.",
            "Pinch tips to encourage bushy growth.",
            "Sweetness is most concentrated just before flowering."
        ],
        "common_problems": [
            "Stem rot in wet conditions.",
            "Aphids: use insecticidal soap."
        ],
        "harvesting": "Harvest leaves just before plant flowers for maximum sweetness. Cut stems and strip leaves.",
        "storage": "Dry leaves in a warm, dark place. Crush dried leaves into powder. Store in airtight containers."
    },
    "Tarragon": {
        "growing_tips": [
            "French tarragon is grown from cuttings or divisions (does not come true from seed).",
            "Needs well-drained soil. Dislikes wet feet.",
            "Divide every 3-4 years to maintain vigor."
        ],
        "common_problems": [
            "Root rot: excellent drainage is essential.",
            "Downy mildew: improve air circulation."
        ],
        "harvesting": "Snip stems as needed. Best flavor before flowering.",
        "storage": "Freeze in oil or vinegar. Does not dry well - flavor is lost. Make tarragon vinegar for long-term storage."
    },
    "Marjoram": {
        "growing_tips": [
            "Start from nursery plants or seeds indoors.",
            "Similar to oregano but more delicate. Not as cold-hardy.",
            "Bring indoors for winter in cold climates."
        ],
        "common_problems": [
            "Root rot: needs good drainage.",
            "Aphids: use insecticidal soap."
        ],
        "harvesting": "Harvest stems before flowers open. Cut back by one-third.",
        "storage": "Dries well. Hang bundles upside down. Store in airtight containers."
    },
    "Sorrel": {
        "growing_tips": [
            "Direct sow in spring or fall. Perennial that returns for years.",
            "Prefers partial shade in hot climates.",
            "Remove flower stalks to prolong leaf production."
        ],
        "common_problems": [
            "Leaf miners: remove affected leaves.",
            "Bolting: remove flower stalks promptly."
        ],
        "harvesting": "Harvest young leaves for best flavor. Older leaves become more sour.",
        "storage": "Refrigerate for 3-5 days. Can be made into soup and frozen."
    },
    "Watercress": {
        "growing_tips": [
            "Grow in shallow water or very moist soil.",
            "Can be grown in containers with saucers of water.",
            "Prefers cool temperatures and partial shade.",
            "Roots easily from stems in water."
        ],
        "common_problems": [
            "Bolting in heat: grow in cool weather or partial shade.",
            "Needs constant moisture."
        ],
        "harvesting": "Cut stems above the waterline. New growth appears quickly.",
        "storage": "Treat like cut herbs - stand in water in the fridge. Use within a few days."
    },
    "Microgreens": {
        "growing_tips": [
            "Grow indoors year-round on shallow trays with a thin layer of soil.",
            "Harvest in 7-14 days when first true leaves appear.",
            "Use any seed: radish, sunflower, pea, broccoli, and beet are popular.",
            "Keep soil moist but not waterlogged. Mist daily."
        ],
        "common_problems": [
            "Mold: caused by poor air circulation or overwatering. Use a small fan.",
            "Damping off: seedlings collapse. Use clean trays and fresh soil."
        ],
        "harvesting": "Cut just above soil level when cotyledons are fully open and first true leaves appear (7-14 days).",
        "storage": "Refrigerate in a container with a paper towel. Use within 5-7 days."
    },
    "Edamame": {
        "growing_tips": [
            "Direct sow after last frost when soil is at least 60F (16C).",
            "Same growing needs as other soybeans.",
            "Does not need nitrogen fertilizer - fixes its own.",
            "Grows best in full sun with regular water."
        ],
        "common_problems": [
            "Rabbits and deer: use fencing.",
            "Stink bugs: can cause dimpled pods.",
            "Mexican bean beetle: hand-pick."
        ],
        "harvesting": "Harvest when pods are plump but still bright green. Pull the whole plant or pick individual pods.",
        "storage": "Blanch and freeze immediately for best quality. Refrigerate fresh pods for 2-3 days."
    },
    "Tomatillo": {
        "growing_tips": [
            "Start seeds indoors 6-8 weeks before last frost.",
            "Plant at least 2 plants for cross-pollination.",
            "Grows like a tomato but more vigorous - cage or stake.",
            "Let fruits fall to the ground naturally - they are ripe when the husk splits."
        ],
        "common_problems": [
            "Poor fruit set: need 2+ plants for pollination.",
            "Same pests as tomatoes: hornworms, aphids.",
            "Can self-seed aggressively."
        ],
        "harvesting": "Harvest when husks split open and fruit fills the husk. Fruits should be firm and bright green (or purple depending on variety).",
        "storage": "Leave in husks and refrigerate for 2-3 weeks. Remove husks, wash off sticky coating, and freeze for salsa verde."
    },
    "Ground Cherry": {
        "growing_tips": [
            "Start seeds indoors 6-8 weeks before last frost.",
            "Similar to tomatillos but more compact.",
            "Fruits drop when ripe - lay mulch to keep them clean.",
            "Very productive plants."
        ],
        "common_problems": [
            "Self-seeds aggressively. Can become weedy.",
            "Same pests as other nightshades."
        ],
        "harvesting": "Let fruits fall from the plant. They are ripe when the husk turns tan and the fruit is golden-orange.",
        "storage": "Leave in husks at room temperature for 2-4 weeks. Remove husks and refrigerate for about a week."
    },
    "Passion Fruit": {
        "growing_tips": [
            "Grow on a sturdy trellis or fence. Vigorous climber.",
            "Needs frost-free conditions or grow in a large container to bring indoors.",
            "Plant 2 varieties if growing non-self-fertile types."
        ],
        "common_problems": [
            "Frost damage: not cold-hardy at all.",
            "Fusarium wilt: use grafted plants.",
            "Fruit fly: use traps."
        ],
        "harvesting": "Harvest when fruits fall from the vine. Wrinkled skin indicates full ripeness.",
        "storage": "Ripen on the counter until wrinkled. Refrigerate for 1-2 weeks. Scoop out pulp and freeze."
    },
    "Horseradish": {
        "growing_tips": [
            "Plant root cuttings in spring. Very easy to grow.",
            "Plant in a contained area - it spreads aggressively.",
            "Grows in almost any soil condition."
        ],
        "common_problems": [
            "Invasiveness: very hard to eradicate. Use root barriers.",
            "Flea beetles: cosmetic damage only."
        ],
        "harvesting": "Dig roots in late fall after a frost for strongest flavor. Or harvest anytime during the growing season.",
        "storage": "Refrigerate whole roots for 1-3 months. Grate fresh and mix with vinegar to preserve. Loses potency over time."
    },
    "Romanesco": {
        "growing_tips": [
            "Same growing requirements as cauliflower.",
            "Start seeds indoors 6-8 weeks before last frost.",
            "Needs consistent cool temperatures and even moisture."
        ],
        "common_problems": [
            "Same as cauliflower: sensitive to temperature swings.",
            "Buttoning and brassica pests."
        ],
        "harvesting": "Harvest when the head is fully formed but before florets separate. Cut at the base.",
        "storage": "Refrigerate for 1-2 weeks. Blanch and freeze."
    },
    "Radicchio": {
        "growing_tips": [
            "Direct sow in mid-summer for fall harvest.",
            "Needs cool weather to form tight heads.",
            "Can tolerate light frost."
        ],
        "common_problems": [
            "Bolting in heat: plant for fall harvest.",
            "Slugs and aphids."
        ],
        "harvesting": "Harvest when heads are firm and colorful. Cut at the base.",
        "storage": "Refrigerate for 2-3 weeks. Flavor mellows slightly in storage."
    },
    "Parsnip": {
        "growing_tips": [
            "Direct sow in spring. Very slow to germinate (2-4 weeks).",
            "Needs deep, loose, stone-free soil for long roots.",
            "Flavor improves dramatically after frost.",
            "Leave in the ground and harvest through winter."
        ],
        "common_problems": [
            "Slow germination: use fresh seed only. Keep soil moist.",
            "Canker: brown spots on roots. Grow resistant varieties.",
            "Carrot fly: use row covers."
        ],
        "harvesting": "Harvest after several frosts for the sweetest flavor. Dig carefully to avoid breaking the long root.",
        "storage": "Leave in the ground mulched with straw for winter harvest. Refrigerate for 2-4 weeks. Can be frozen after cooking."
    },
    "Lovage": {
        "growing_tips": [
            "Perennial herb that grows 4-6 feet tall.",
            "Tastes like intense celery. A little goes a long way.",
            "Start from nursery plants or divide established clumps."
        ],
        "common_problems": [
            "Leaf miners: remove affected leaves.",
            "Can become very large - give it space."
        ],
        "harvesting": "Harvest young leaves for salads, older leaves for cooking. Use stems like celery in soups.",
        "storage": "Refrigerate leaves for a few days. Freeze in ice cube trays with water. Dries reasonably well."
    },
    "Lemon Balm": {
        "growing_tips": [
            "Very easy to grow - can become invasive.",
            "Cut back regularly to prevent spreading.",
            "Remove flower stalks to prolong leaf production.",
            "Excellent in containers."
        ],
        "common_problems": [
            "Invasiveness: spreads by seed and runners. Deadhead and contain.",
            "Powdery mildew: improve air circulation."
        ],
        "harvesting": "Harvest leaves anytime. Best flavor just before flowering.",
        "storage": "Refrigerate in a bag for a few days. Dries well for tea. Freeze in ice cubes."
    },
}


@plants_bp.route("/<int:plant_id>/care-tips", methods=["GET"])
def get_plant_care_tips(plant_id):
    """Return detailed growing tips, common problems, harvesting advice,
    and storage tips for a specific plant."""
    plant = Plant.query.get_or_404(plant_id)

    tips = CARE_TIPS.get(plant.name)

    if not tips:
        # Generate generic tips based on plant attributes
        generic_tips = {
            "growing_tips": [],
            "common_problems": [],
            "harvesting": "Harvest when the plant reaches maturity according to its growing season.",
            "storage": "Store in a cool, dry place or refrigerate for short-term storage."
        }

        if plant.sunlight:
            generic_tips["growing_tips"].append(f"Provide {plant.sunlight.lower()} conditions.")
        if plant.water_needs:
            generic_tips["growing_tips"].append(f"Water needs: {plant.water_needs.lower()}. Adjust based on weather and soil moisture.")
        if plant.growing_season:
            generic_tips["growing_tips"].append(f"Best grown in {plant.growing_season.lower()}. Plan accordingly based on your zone.")
        if plant.sowing_method:
            generic_tips["growing_tips"].append(f"Sowing method: {plant.sowing_method}.")
        if plant.suitable_for_containers:
            generic_tips["growing_tips"].append("Suitable for container growing.")
        if plant.requires_greenhouse:
            generic_tips["growing_tips"].append("May require greenhouse growing in cooler climates.")
        if plant.space_required:
            generic_tips["growing_tips"].append(f"Space required: {plant.space_required.lower()}.")

        if not generic_tips["growing_tips"]:
            generic_tips["growing_tips"].append("Follow general gardening best practices for this plant type.")

        generic_tips["common_problems"].append("Monitor for common garden pests such as aphids, slugs, and caterpillars.")
        generic_tips["common_problems"].append("Ensure proper spacing and air circulation to prevent fungal diseases.")
        generic_tips["common_problems"].append("Water consistently to avoid stress-related problems.")

        tips = generic_tips

    return jsonify({
        "plant_id": plant.id,
        "plant_name": plant.name,
        "care_tips": tips,
    }), 200