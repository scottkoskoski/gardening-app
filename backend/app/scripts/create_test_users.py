# app/scripts/create_test_users.py
from app import create_app
from app.models.database import db
from app.models.user import User
from app.models.profile import UserProfile

def create_test_users():
    app = create_app()
    with app.app_context():
        # Creating test user
        test_user = User(username="gardener", email="gardener@example.com")
        test_user.set_password("GardenPassword123!")
        db.session.add(test_user)
        db.session.flush() # Flush to get the user ID
        
        # Create user profile
        profile = UserProfile(
            user_id=test_user.id,
            plant_hardiness_zone="7a",
            zip_code="10001",
            city="New York",
            state="NY"
        )
        db.session.add(profile)
        db.session.commit()
        print(f"Test user created with ID: {test_user.id}")

if __name__ == "__main__":
    create_test_users()