from ..models.database import db
from ..models.garden_type import GardenType
from app import create_app

def populate_garden_types():
    """Adds predefined garden types to the database."""
    app = create_app()
    with app.app_context():
        garden_types = [
            {"enum": GardenType.RAISED_BED, "description": "A garden bed elevated above the ground", "ideal_soil_type": "Loamy", "space_requirements": "Medium", "maintenance_level": "Medium"},
            {"enum": GardenType.CONTAINER, "description": "Plants grown in pots or containers", "ideal_soil_type": "Potting mix", "space_requirements": "Small", "maintenance_level": "Low"},
            {"enum": GardenType.TRADITIONAL_ROW, "description": "Plants grown in rows directly in soil", "ideal_soil_type": "Sandy loam", "space_requirements": "Large", "maintenance_level": "High"},
            {"enum": GardenType.VERTICAL, "description": "Gardening using vertical space with trellises or stacked planters", "ideal_soil_type": "Varies", "space_requirements": "Small", "maintenance_level": "Medium"},
            {"enum": GardenType.GREENHOUSE, "description": "Indoor controlled environment for year-round growing", "ideal_soil_type": "Custom blends", "space_requirements": "Varies", "maintenance_level": "High"},
            {"enum": GardenType.HYDROPONIC, "description": "Soilless gardening using water and nutrients", "ideal_soil_type": "None", "space_requirements": "Small to Medium", "maintenance_level": "High"},
            {"enum": GardenType.PERMACULTURE, "description": "A self-sustaining, biodiverse garden system", "ideal_soil_type": "Rich organic", "space_requirements": "Large", "maintenance_level": "High"},
            {"enum": GardenType.COMMUNITY, "description": "A shared gardening space", "ideal_soil_type": "Varies", "space_requirements": "Large", "maintenance_level": "Medium"},
            {"enum": GardenType.WILDLIFE_GARDEN, "description": "Designed to attract and support wildlife", "ideal_soil_type": "Native soil", "space_requirements": "Medium to Large", "maintenance_level": "Low"},
            {"enum": GardenType.ROOFTOP, "description": "Gardening on rooftops or terraces", "ideal_soil_type": "Lightweight soil mix", "space_requirements": "Small to Medium", "maintenance_level": "Medium"},
        ]
            
        for garden in garden_types:
            existing = GardenType.query.filter_by(name=garden["name"]).first()
            if not existing:
                new_garden_type = GardenType(
                    name=garden["name"].name,
                    description=garden["description"],
                    ideal_soil_type=garden["ideal_soil_type"],
                    space_requirements=garden["space_requirements"],
                    maintenance_level=garden["maintenance_level"]
                )
                db.session.add(new_garden_type)

        db.session.commit()
        print("Garden types have been added to the database!")

if __name__ == "__main__":
    populate_garden_types()
