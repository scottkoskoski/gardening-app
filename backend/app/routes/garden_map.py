from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models.database import db
from ..models.user_garden import UserGarden
from ..models.user_garden_plant import UserGardenPlant, GrowthStage
from ..models.plant import Plant

garden_map_bp = Blueprint("garden_map", __name__)

# Companion planting data: plant_name -> {good_companions: [...], bad_companions: [...], tips: str}
COMPANION_DATA = {
    "Artichoke": {
        "good": ["Sunflower", "Tarragon", "Pea"],
        "bad": [],
        "tips": "Artichokes are large plants; give them plenty of space and pair with nitrogen-fixers like peas."
    },
    "Arugula": {
        "good": ["Carrot", "Beet", "Lettuce", "Onion", "Dill"],
        "bad": ["Strawberry"],
        "tips": "Arugula grows quickly and can be tucked between slower crops as a living mulch."
    },
    "Asparagus": {
        "good": ["Tomato", "Parsley", "Basil", "Marigold", "Dill"],
        "bad": ["Onion", "Garlic", "Potato"],
        "tips": "Asparagus and tomatoes are classic companions - tomatoes repel asparagus beetles."
    },
    "Basil": {
        "good": ["Tomato", "Pepper", "Oregano", "Lettuce", "Asparagus", "Marigold"],
        "bad": ["Sage", "Thyme"],
        "tips": "Plant near tomatoes and peppers. Basil can repel aphids and mosquitoes."
    },
    "Bay Laurel": {
        "good": ["Rosemary", "Lavender", "Thyme"],
        "bad": [],
        "tips": "Bay laurel pairs well with other Mediterranean herbs that share similar growing needs."
    },
    "Beet": {
        "good": ["Lettuce", "Onion", "Garlic", "Cabbage", "Kohlrabi", "Broccoli"],
        "bad": ["Green Bean", "Mustard"],
        "tips": "Beets and onions make great companions. The beet greens provide ground cover."
    },
    "Bell Pepper": {
        "good": ["Basil", "Tomato", "Carrot", "Onion", "Spinach", "Marigold"],
        "bad": ["Fennel", "Green Bean", "Kohlrabi"],
        "tips": "Bell peppers love basil nearby - it may improve flavor and repel common pests."
    },
    "Blackberry": {
        "good": ["Borage", "Mint", "Garlic", "Chives", "Tansy"],
        "bad": ["Tomato", "Pepper", "Eggplant", "Potato", "Raspberry"],
        "tips": "Keep blackberries away from nightshades to avoid shared diseases. Borage attracts pollinators."
    },
    "Blueberry": {
        "good": ["Strawberry", "Rhododendron", "Azalea", "Thyme"],
        "bad": ["Tomato", "Pepper"],
        "tips": "Blueberries love acidic soil. Pair with other acid-loving plants."
    },
    "Bok Choy": {
        "good": ["Celery", "Onion", "Beet", "Thyme", "Chamomile"],
        "bad": ["Strawberry", "Tomato"],
        "tips": "Bok choy grows well with alliums that help repel cabbage pests."
    },
    "Borage": {
        "good": ["Tomato", "Cucumber", "Squash", "Strawberry", "Cabbage"],
        "bad": [],
        "tips": "Borage is a powerful pollinator attractor and may improve the flavor of nearby tomatoes and strawberries."
    },
    "Broccoli": {
        "good": ["Beet", "Celery", "Chamomile", "Dill", "Onion", "Rosemary", "Sage"],
        "bad": ["Tomato", "Strawberry", "Hot Pepper"],
        "tips": "Aromatic herbs like rosemary and sage repel cabbage moths that attack broccoli."
    },
    "Brussels Sprouts": {
        "good": ["Beet", "Carrot", "Dill", "Onion", "Sage", "Thyme"],
        "bad": ["Strawberry", "Tomato"],
        "tips": "Plant with strong-scented herbs to deter cabbage white butterflies."
    },
    "Butternut Squash": {
        "good": ["Corn", "Green Bean", "Radish", "Marigold", "Nasturtium", "Borage"],
        "bad": ["Potato"],
        "tips": "A classic Three Sisters crop. Large leaves shade soil and suppress weeds."
    },
    "Cabbage": {
        "good": ["Beet", "Celery", "Chamomile", "Dill", "Onion", "Rosemary", "Sage", "Thyme"],
        "bad": ["Strawberry", "Tomato", "Grape"],
        "tips": "Cabbage benefits from aromatic herbs and alliums that confuse cabbage moths."
    },
    "Calendula": {
        "good": ["Tomato", "Pepper", "Asparagus", "Cucumber", "Pea"],
        "bad": [],
        "tips": "Calendula attracts beneficial insects and can serve as a trap crop for aphids."
    },
    "Cantaloupe": {
        "good": ["Corn", "Sunflower", "Nasturtium", "Radish", "Marigold"],
        "bad": ["Potato", "Cucumber"],
        "tips": "Melons need space. Nasturtiums help repel cucumber beetles."
    },
    "Carrot": {
        "good": ["Tomato", "Lettuce", "Onion", "Pea", "Radish", "Rosemary", "Chives", "Sage"],
        "bad": ["Dill", "Celery", "Parsnip"],
        "tips": "Carrots grow well with onions - onions repel carrot fly."
    },
    "Cauliflower": {
        "good": ["Beet", "Celery", "Dill", "Onion", "Spinach", "Sage"],
        "bad": ["Strawberry", "Tomato"],
        "tips": "Similar to broccoli companions. Celery deters cabbage white butterflies."
    },
    "Celery": {
        "good": ["Tomato", "Cabbage", "Cauliflower", "Leek", "Spinach", "Onion"],
        "bad": ["Carrot", "Parsnip", "Corn"],
        "tips": "Celery and tomatoes or brassicas are mutually beneficial companions."
    },
    "Chamomile": {
        "good": ["Cabbage", "Broccoli", "Cauliflower", "Onion", "Cucumber"],
        "bad": [],
        "tips": "Chamomile improves the health and flavor of brassicas and attracts beneficial insects."
    },
    "Cherry Tomato": {
        "good": ["Basil", "Carrot", "Parsley", "Marigold", "Lettuce", "Onion", "Chives"],
        "bad": ["Cabbage", "Fennel", "Potato", "Corn"],
        "tips": "Same companions as regular tomatoes. Basil may enhance flavor and repel pests."
    },
    "Chives": {
        "good": ["Carrot", "Tomato", "Rose", "Strawberry", "Apple"],
        "bad": ["Green Bean", "Pea"],
        "tips": "Chives repel aphids and carrot fly. Excellent border plant."
    },
    "Cilantro": {
        "good": ["Tomato", "Pepper", "Spinach", "Lettuce", "Pea", "Anise"],
        "bad": ["Fennel"],
        "tips": "Cilantro attracts beneficial insects when it bolts and flowers."
    },
    "Collard Greens": {
        "good": ["Onion", "Garlic", "Beet", "Rosemary", "Thyme", "Dill"],
        "bad": ["Strawberry", "Tomato"],
        "tips": "Alliums and aromatic herbs help repel cabbage family pests."
    },
    "Comfrey": {
        "good": ["Fruit trees", "Raspberry", "Strawberry", "Grape"],
        "bad": [],
        "tips": "Comfrey is a dynamic accumulator - its deep roots pull up nutrients. Excellent mulch plant."
    },
    "Corn": {
        "good": ["Green Bean", "Squash", "Cucumber", "Pea", "Cantaloupe", "Watermelon", "Pumpkin"],
        "bad": ["Tomato", "Celery"],
        "tips": "The classic 'Three Sisters' planting: corn, beans, and squash support each other."
    },
    "Cosmos": {
        "good": ["Tomato", "Squash", "Cucumber"],
        "bad": [],
        "tips": "Cosmos attract pollinators and beneficial insects like lacewings and parasitic wasps."
    },
    "Cucumber": {
        "good": ["Green Bean", "Pea", "Radish", "Sunflower", "Lettuce", "Corn", "Dill", "Nasturtium"],
        "bad": ["Potato", "Sage", "Mint"],
        "tips": "Train cucumbers to grow up trellises near corn for natural support."
    },
    "Dill": {
        "good": ["Cabbage", "Lettuce", "Onion", "Cucumber", "Broccoli", "Tomato"],
        "bad": ["Carrot"],
        "tips": "Dill attracts beneficial wasps and ladybugs. Young dill benefits tomatoes; harvest before it goes to seed near them. Keep away from carrots (cross-pollination risk)."
    },
    "Eggplant": {
        "good": ["Green Bean", "Pepper", "Spinach", "Thyme", "Marigold"],
        "bad": ["Fennel"],
        "tips": "Eggplant benefits from beans (nitrogen) and marigolds (pest deterrent)."
    },
    "Endive": {
        "good": ["Carrot", "Radish", "Onion", "Chives"],
        "bad": [],
        "tips": "Endive pairs well with root vegetables and alliums."
    },
    "Fennel": {
        "good": ["Dill"],
        "bad": ["Tomato", "Pepper", "Green Bean", "Carrot", "Eggplant", "Kohlrabi"],
        "tips": "Fennel is allelopathic and inhibits many plants. Grow it isolated or with dill."
    },
    "Garlic": {
        "good": ["Tomato", "Pepper", "Lettuce", "Beet", "Strawberry", "Rose", "Raspberry"],
        "bad": ["Green Bean", "Pea"],
        "tips": "Garlic is a natural pest deterrent. Plant around roses and vegetables."
    },
    "Ginger": {
        "good": ["Cilantro", "Lemongrass", "Turmeric", "Green Bean"],
        "bad": [],
        "tips": "Ginger grows well with other tropical plants and benefits from partial shade."
    },
    "Grape": {
        "good": ["Chives", "Garlic", "Rosemary", "Hyssop", "Geranium"],
        "bad": ["Cabbage", "Radish"],
        "tips": "Grapes benefit from alliums and aromatic herbs that deter Japanese beetles."
    },
    "Green Bean": {
        "good": ["Corn", "Cucumber", "Potato", "Carrot", "Pea", "Squash", "Eggplant"],
        "bad": ["Onion", "Garlic", "Pepper", "Fennel", "Chives"],
        "tips": "Beans fix nitrogen in the soil, benefiting neighboring plants."
    },
    "Green Onion": {
        "good": ["Carrot", "Lettuce", "Tomato", "Beet", "Strawberry", "Pepper"],
        "bad": ["Green Bean", "Pea"],
        "tips": "Green onions repel pests and fit neatly between other crops."
    },
    "Horseradish": {
        "good": ["Potato", "Sweet Potato"],
        "bad": [],
        "tips": "Horseradish planted at potato patch corners may repel Colorado potato beetles."
    },
    "Hot Pepper": {
        "good": ["Basil", "Tomato", "Carrot", "Onion", "Spinach", "Marigold"],
        "bad": ["Fennel", "Green Bean", "Broccoli"],
        "tips": "Hot peppers benefit from the same companions as bell peppers."
    },
    "Jalapeno Pepper": {
        "good": ["Basil", "Tomato", "Carrot", "Onion", "Spinach", "Marigold"],
        "bad": ["Fennel", "Green Bean"],
        "tips": "Same companion guidelines as other peppers. Basil helps repel aphids."
    },
    "Kale": {
        "good": ["Beet", "Celery", "Cucumber", "Dill", "Garlic", "Lettuce", "Onion", "Spinach"],
        "bad": ["Strawberry", "Tomato"],
        "tips": "Kale benefits from alliums and aromatic herbs. Interplant with lettuce for efficient space use."
    },
    "Kohlrabi": {
        "good": ["Beet", "Onion", "Cucumber", "Lettuce"],
        "bad": ["Tomato", "Pepper", "Fennel", "Strawberry"],
        "tips": "Kohlrabi pairs well with other brassica companions like beets and onions."
    },
    "Lavender": {
        "good": ["Rose", "Rosemary", "Thyme", "Sage", "Oregano"],
        "bad": ["Mint"],
        "tips": "Lavender repels fleas, moths, and mosquitoes. Attracts pollinators."
    },
    "Leek": {
        "good": ["Carrot", "Celery", "Onion", "Strawberry"],
        "bad": ["Green Bean", "Pea"],
        "tips": "Leeks repel carrot fly and work well interplanted with carrots."
    },
    "Lemon Balm": {
        "good": ["Tomato", "Squash", "Melon", "Broccoli"],
        "bad": [],
        "tips": "Lemon balm attracts pollinators and repels mosquitoes. Can be invasive - contain it."
    },
    "Lemongrass": {
        "good": ["Ginger", "Turmeric", "Cilantro", "Tomato"],
        "bad": [],
        "tips": "Lemongrass repels mosquitoes and pairs well with tropical edibles."
    },
    "Lettuce": {
        "good": ["Carrot", "Radish", "Strawberry", "Onion", "Garlic", "Beet", "Chives"],
        "bad": ["Celery", "Parsley"],
        "tips": "Lettuce benefits from taller plants nearby that provide partial shade."
    },
    "Marigold": {
        "good": ["Tomato", "Pepper", "Cucumber", "Squash", "Potato", "Eggplant", "Rose"],
        "bad": ["Green Bean", "Cabbage"],
        "tips": "Marigolds repel nematodes, aphids, and whiteflies. Plant throughout the garden."
    },
    "Marjoram": {
        "good": ["Pepper", "Eggplant", "Squash", "Green Bean"],
        "bad": [],
        "tips": "Marjoram improves the flavor of nearby vegetables and attracts pollinators."
    },
    "Mint": {
        "good": ["Cabbage", "Tomato", "Pea"],
        "bad": ["Lavender", "Chamomile", "Parsley"],
        "tips": "Mint repels cabbage moths and ants. Always grow in containers to prevent spreading."
    },
    "Nasturtium": {
        "good": ["Cucumber", "Squash", "Tomato", "Cabbage", "Radish", "Green Bean"],
        "bad": [],
        "tips": "Nasturtium is an excellent trap crop for aphids. Flowers are edible."
    },
    "Okra": {
        "good": ["Pepper", "Eggplant", "Melon", "Cucumber", "Basil"],
        "bad": [],
        "tips": "Okra provides shade for heat-sensitive crops. Pairs well with other warm-season plants."
    },
    "Onion": {
        "good": ["Carrot", "Lettuce", "Tomato", "Pepper", "Beet", "Strawberry", "Cabbage"],
        "bad": ["Green Bean", "Pea"],
        "tips": "Onions repel many pests and pair well with most garden vegetables."
    },
    "Oregano": {
        "good": ["Basil", "Pepper", "Tomato", "Squash", "Grape"],
        "bad": [],
        "tips": "Oregano provides ground cover and repels aphids. Great near peppers and tomatoes."
    },
    "Parsley": {
        "good": ["Tomato", "Asparagus", "Corn", "Pepper", "Rose"],
        "bad": ["Lettuce", "Mint"],
        "tips": "Parsley attracts beneficial insects and pairs well with tomatoes and asparagus."
    },
    "Parsnip": {
        "good": ["Radish", "Onion", "Garlic", "Pea", "Green Bean"],
        "bad": ["Carrot", "Celery"],
        "tips": "Parsnips grow well with alliums. Radishes help mark the slow-germinating rows."
    },
    "Pea": {
        "good": ["Carrot", "Corn", "Cucumber", "Green Bean", "Radish", "Turnip", "Spinach"],
        "bad": ["Onion", "Garlic", "Chives"],
        "tips": "Peas fix nitrogen in the soil. Follow peas with nitrogen-loving crops."
    },
    "Pepper": {
        "good": ["Basil", "Tomato", "Carrot", "Onion", "Spinach", "Marigold"],
        "bad": ["Fennel", "Green Bean"],
        "tips": "Peppers and basil are great companions. Basil may improve pepper flavor."
    },
    "Peppermint": {
        "good": ["Cabbage", "Broccoli", "Kale"],
        "bad": ["Lavender", "Chamomile"],
        "tips": "Peppermint deters cabbage moths and flea beetles. Grow in pots to contain spreading."
    },
    "Potato": {
        "good": ["Green Bean", "Corn", "Cabbage", "Pea", "Marigold", "Horseradish"],
        "bad": ["Tomato", "Cucumber", "Squash", "Sunflower", "Raspberry"],
        "tips": "Keep potatoes away from tomatoes - they share diseases (late blight)."
    },
    "Pumpkin": {
        "good": ["Corn", "Green Bean", "Radish", "Marigold", "Nasturtium", "Sunflower"],
        "bad": ["Potato"],
        "tips": "Another great Three Sisters crop. Nasturtiums repel squash bugs."
    },
    "Radicchio": {
        "good": ["Carrot", "Onion", "Lettuce", "Chives"],
        "bad": [],
        "tips": "Radicchio pairs well with other salad greens and alliums."
    },
    "Radish": {
        "good": ["Carrot", "Lettuce", "Pea", "Cucumber", "Spinach", "Nasturtium", "Chives"],
        "bad": [],
        "tips": "Fast-growing radishes mark rows for slow-germinating carrots."
    },
    "Raspberry": {
        "good": ["Garlic", "Marigold", "Tansy", "Turnip"],
        "bad": ["Blackberry", "Potato"],
        "tips": "Garlic deters Japanese beetles. Keep raspberries away from other brambles."
    },
    "Rhubarb": {
        "good": ["Garlic", "Onion", "Cabbage", "Kale", "Strawberry"],
        "bad": [],
        "tips": "Rhubarb leaves deter pests (never eat the leaves). Pairs with brassicas."
    },
    "Romaine Lettuce": {
        "good": ["Carrot", "Radish", "Strawberry", "Onion", "Garlic", "Beet", "Chives"],
        "bad": ["Celery", "Parsley"],
        "tips": "Same companion guidelines as regular lettuce. Benefits from afternoon shade."
    },
    "Rose": {
        "good": ["Garlic", "Chives", "Lavender", "Marigold", "Parsley", "Geranium"],
        "bad": [],
        "tips": "Garlic and chives repel aphids from roses. Lavender attracts pollinators."
    },
    "Rosemary": {
        "good": ["Sage", "Lavender", "Thyme", "Cabbage", "Broccoli", "Carrot", "Green Bean"],
        "bad": [],
        "tips": "Rosemary repels cabbage moths, carrot fly, and bean beetles."
    },
    "Sage": {
        "good": ["Rosemary", "Cabbage", "Carrot", "Tomato", "Strawberry"],
        "bad": ["Cucumber", "Basil"],
        "tips": "Sage repels cabbage moths and carrot flies. Avoid planting near cucumbers."
    },
    "Spinach": {
        "good": ["Strawberry", "Pea", "Green Bean", "Radish", "Pepper", "Kale", "Lettuce"],
        "bad": [],
        "tips": "Spinach grows well in the shade of taller plants during hot months."
    },
    "Squash": {
        "good": ["Corn", "Green Bean", "Radish", "Marigold", "Pea", "Nasturtium", "Borage"],
        "bad": ["Potato"],
        "tips": "Large squash leaves shade the ground, suppressing weeds for neighbors."
    },
    "Strawberry": {
        "good": ["Lettuce", "Spinach", "Onion", "Garlic", "Borage", "Thyme", "Sage"],
        "bad": ["Cabbage", "Broccoli", "Fennel"],
        "tips": "Borage is the best strawberry companion - it attracts pollinators and may improve yield."
    },
    "Sugar Snap Pea": {
        "good": ["Carrot", "Corn", "Cucumber", "Green Bean", "Radish", "Turnip"],
        "bad": ["Onion", "Garlic"],
        "tips": "Same companions as regular peas. Great nitrogen fixer for the soil."
    },
    "Sunchoke": {
        "good": ["Corn", "Sunflower"],
        "bad": ["Tomato"],
        "tips": "Sunchokes grow tall and can shade other plants. Give them their own area."
    },
    "Sunflower": {
        "good": ["Cucumber", "Corn", "Squash", "Lettuce", "Pumpkin"],
        "bad": ["Potato"],
        "tips": "Sunflowers attract pollinators and provide natural trellising for climbing crops."
    },
    "Sweet Potato": {
        "good": ["Green Bean", "Thyme", "Oregano", "Dill", "Horseradish"],
        "bad": ["Squash", "Tomato"],
        "tips": "Sweet potato vines provide ground cover. Pair with herbs that repel pests."
    },
    "Swiss Chard": {
        "good": ["Green Bean", "Onion", "Cabbage", "Lettuce", "Lavender"],
        "bad": ["Corn", "Cucumber"],
        "tips": "Swiss chard does well with brassicas and alliums. Attractive as an edible border."
    },
    "Tarragon": {
        "good": ["Tomato", "Eggplant", "Pepper"],
        "bad": [],
        "tips": "Tarragon improves the flavor and growth of neighboring vegetables."
    },
    "Thyme": {
        "good": ["Cabbage", "Broccoli", "Eggplant", "Potato", "Strawberry", "Rose", "Lavender"],
        "bad": ["Basil"],
        "tips": "Thyme repels cabbage worms, whiteflies, and corn earworms."
    },
    "Tomatillo": {
        "good": ["Basil", "Carrot", "Parsley", "Marigold", "Pepper"],
        "bad": ["Fennel", "Potato", "Corn", "Dill"],
        "tips": "Tomatillos need cross-pollination - plant at least two. Similar companions to tomatoes."
    },
    "Tomato": {
        "good": ["Basil", "Carrot", "Parsley", "Marigold", "Lettuce", "Onion", "Chives", "Borage", "Nasturtium", "Dill"],
        "bad": ["Cabbage", "Fennel", "Potato", "Corn"],
        "tips": "Tomatoes love basil as a companion - it may improve flavor and repel pests. Young dill attracts beneficial insects, though mature dill may slightly inhibit tomato growth."
    },
    "Turmeric": {
        "good": ["Ginger", "Lemongrass", "Cilantro", "Green Bean"],
        "bad": [],
        "tips": "Turmeric grows well with other tropical plants and benefits from partial shade."
    },
    "Turnip": {
        "good": ["Pea", "Onion", "Garlic", "Vetch"],
        "bad": ["Potato", "Mustard"],
        "tips": "Turnips pair well with peas. Onions and garlic help deter turnip pests."
    },
    "Watermelon": {
        "good": ["Corn", "Sunflower", "Nasturtium", "Radish", "Marigold"],
        "bad": ["Potato", "Cucumber"],
        "tips": "Watermelons need space. Nasturtiums help repel beetles."
    },
    "Winter Squash": {
        "good": ["Corn", "Green Bean", "Radish", "Marigold", "Nasturtium", "Borage"],
        "bad": ["Potato"],
        "tips": "Classic Three Sisters companion. Large leaves suppress weeds."
    },
    "Zucchini": {
        "good": ["Corn", "Green Bean", "Radish", "Marigold", "Nasturtium", "Borage", "Pea"],
        "bad": ["Potato"],
        "tips": "Zucchini benefits from borage to attract pollinators and nasturtiums to repel squash bugs."
    },
    # Aliases for generic lookups
    "Bean": {
        "good": ["Corn", "Cucumber", "Potato", "Carrot", "Pea", "Squash", "Eggplant"],
        "bad": ["Onion", "Garlic", "Pepper", "Fennel"],
        "tips": "Beans fix nitrogen in the soil, benefiting neighboring plants."
    },
    "Melon": {
        "good": ["Corn", "Sunflower", "Nasturtium", "Radish", "Marigold"],
        "bad": ["Potato", "Cucumber"],
        "tips": "Melons need space. Plant with nasturtiums and marigolds for pest control."
    },
}


def _get_companion_info(plant_name, all_placed_names):
    """Get companion planting recommendations for a plant given its garden neighbors."""
    data = COMPANION_DATA.get(plant_name, None)
    good_neighbors = []
    bad_neighbors = []
    tips = []

    if data:
        tips.append(data["tips"])
        for neighbor in all_placed_names:
            if neighbor == plant_name:
                continue
            if neighbor in data["good"]:
                good_neighbors.append(neighbor)
            if neighbor in data["bad"]:
                bad_neighbors.append(neighbor)

    return {
        "good_companions": good_neighbors,
        "bad_companions": bad_neighbors,
        "tips": tips
    }


@garden_map_bp.route("/<int:garden_id>/map", methods=["GET"])
@jwt_required()
def get_garden_map(garden_id):
    """Get garden map data including grid dimensions and all placed plants."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()

    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    placements = []
    for gp in garden.garden_plants:
        placement = {
            "id": gp.id,
            "plant_id": gp.plant_id,
            "plant_name": gp.plant.name,
            "growth_stage": gp.growth_stage.value,
            "row": gp.row,
            "col": gp.col,
            "image_url": gp.plant.image_url,
            "expected_harvest_date": gp.expected_harvest_date.isoformat() if gp.expected_harvest_date else None,
        }
        placements.append(placement)

    return jsonify({
        "garden_id": garden.id,
        "garden_name": garden.garden_name,
        "grid_rows": garden.grid_rows or 8,
        "grid_cols": garden.grid_cols or 10,
        "placements": placements,
    }), 200


@garden_map_bp.route("/<int:garden_id>/map/resize", methods=["PUT"])
@jwt_required()
def resize_garden_grid(garden_id):
    """Update garden grid dimensions."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()

    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    data = request.get_json()
    grid_rows = data.get("grid_rows")
    grid_cols = data.get("grid_cols")

    if not grid_rows or not grid_cols:
        return jsonify({"error": "grid_rows and grid_cols are required"}), 400

    if not (1 <= grid_rows <= 50 and 1 <= grid_cols <= 50):
        return jsonify({"error": "Grid dimensions must be between 1 and 50"}), 400

    garden.grid_rows = grid_rows
    garden.grid_cols = grid_cols

    # Remove any plants that fall outside the new grid
    for gp in garden.garden_plants:
        if gp.row is not None and gp.col is not None:
            if gp.row >= grid_rows or gp.col >= grid_cols:
                gp.row = None
                gp.col = None

    db.session.commit()
    return jsonify({"message": "Grid resized successfully"}), 200


@garden_map_bp.route("/<int:garden_id>/map/place", methods=["POST"])
@jwt_required()
def place_plant_on_map(garden_id):
    """Place a new plant on the garden map at a specific grid position."""
    user_id = get_jwt_identity()
    garden = UserGarden.query.filter_by(id=garden_id, user_id=user_id).first()

    if not garden:
        return jsonify({"error": "Garden not found"}), 404

    data = request.get_json()
    plant_id = data.get("plant_id")
    row = data.get("row")
    col = data.get("col")

    if plant_id is None or row is None or col is None:
        return jsonify({"error": "plant_id, row, and col are required"}), 400

    grid_rows = garden.grid_rows or 8
    grid_cols = garden.grid_cols or 10

    if row < 0 or row >= grid_rows or col < 0 or col >= grid_cols:
        return jsonify({"error": "Position is outside the garden grid"}), 400

    plant = Plant.query.get(plant_id)
    if not plant:
        return jsonify({"error": "Plant not found"}), 404

    # Check if cell is already occupied
    existing = UserGardenPlant.query.filter_by(
        garden_id=garden_id, row=row, col=col
    ).first()
    if existing:
        return jsonify({"error": "This cell is already occupied"}), 409

    new_garden_plant = UserGardenPlant(
        garden_id=garden.id,
        plant_id=plant.id,
        growth_stage=GrowthStage[data.get("growth_stage", "SEEDLING").upper()],
        row=row,
        col=col
    )

    db.session.add(new_garden_plant)
    db.session.commit()

    return jsonify({
        "message": "Plant placed successfully",
        "garden_plant_id": new_garden_plant.id,
        "plant_name": plant.name,
        "image_url": plant.image_url,
    }), 201


@garden_map_bp.route("/<int:garden_id>/map/<int:garden_plant_id>", methods=["DELETE"])
@jwt_required()
def remove_plant_from_map(garden_id, garden_plant_id):
    """Remove a plant from the garden map."""
    user_id = int(get_jwt_identity())
    garden_plant = UserGardenPlant.query.get(garden_plant_id)

    if not garden_plant:
        return jsonify({"error": "Plant not found"}), 404

    if garden_plant.garden_id != garden_id:
        return jsonify({"error": "Plant does not belong to this garden"}), 400

    if garden_plant.garden.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(garden_plant)
    db.session.commit()

    return jsonify({"message": "Plant removed from map"}), 200


@garden_map_bp.route("/<int:garden_id>/map/<int:garden_plant_id>/info", methods=["GET"])
@jwt_required()
def get_placed_plant_info(garden_id, garden_plant_id):
    """Get detailed info and recommendations for a plant placed on the map."""
    user_id = int(get_jwt_identity())
    garden_plant = UserGardenPlant.query.get(garden_plant_id)

    if not garden_plant:
        return jsonify({"error": "Plant not found"}), 404

    if garden_plant.garden.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    plant = garden_plant.plant
    garden = garden_plant.garden

    # Get all plant names in this garden for companion analysis
    all_plant_names = [gp.plant.name for gp in garden.garden_plants if gp.id != garden_plant_id]

    companions = _get_companion_info(plant.name, all_plant_names)

    # Build spacing recommendation
    spacing_tips = []
    if plant.spread:
        spacing_tips.append(f"Spread: {plant.spread} cm")
    if plant.row_spacing:
        spacing_tips.append(f"Row spacing: {plant.row_spacing} cm")
    if plant.height:
        spacing_tips.append(f"Height: {plant.height} cm")

    return jsonify({
        "plant": {
            "id": plant.id,
            "name": plant.name,
            "scientific_name": plant.scientific_name,
            "description": plant.description,
            "image_url": plant.image_url,
            "sunlight": plant.sunlight,
            "water_needs": plant.water_needs,
            "growing_season": plant.growing_season,
            "space_required": plant.space_required,
            "sowing_method": plant.sowing_method,
            "spread": plant.spread,
            "row_spacing": plant.row_spacing,
            "height": plant.height,
            "hardiness_min": plant.hardiness_min,
            "hardiness_max": plant.hardiness_max,
        },
        "placement": {
            "id": garden_plant.id,
            "row": garden_plant.row,
            "col": garden_plant.col,
            "growth_stage": garden_plant.growth_stage.value,
            "planted_at": garden_plant.planted_at.isoformat() if garden_plant.planted_at else None,
            "expected_harvest_date": garden_plant.expected_harvest_date.isoformat() if garden_plant.expected_harvest_date else None,
        },
        "companions": companions,
        "spacing": spacing_tips,
    }), 200
