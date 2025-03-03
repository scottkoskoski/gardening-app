# app/scripts/verify_garden_types.py
from app import create_app
from app.models.garden_type import GardenType

def verify_garden_types():
    app = create_app()
    with app.app_context():
        garden_types = GardenType.query.all()
        print(f"Found {len(garden_types)} garden types:")
        for garden_type in garden_types:
            print(f" - {garden_type.name.value}: {garden_type.description}")

if __name__ == "__main__":
    verify_garden_types()