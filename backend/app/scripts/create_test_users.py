# app/scripts/create_test_users.py
from app import create_app
from app.models.database import db
from app.models.user import User
from app.models.profile import UserProfile

def create_test_users():
    app = create_app()
    with app.app_context():
        # Checking if users already exist to avoid duplicates
        if User.query.filter_by(username="gardener").first():
            print("Test users already exist. Skipping creation.")
            return
        
        # Creating regular test user
        test_user = User(username="gardener", email="gardener@example.com", is_admin=False)
        test_user.set_password("GardenPassword123!")
        db.session.add(test_user)
        db.session.flush() # Flush to get the user ID
        
        # Creating regular user profile
        profile = UserProfile(
            user_id=test_user.id,
            plant_hardiness_zone="7a",
            zip_code="10001",
            city="New York",
            state="NY"
        )
        db.session.add(profile)
        
        # Creating admin test user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            is_admin=True
        )
        admin_user.set_password("AdminPassword123!")
        db.session.add(admin_user)
        db.session.flush() # Flushing to get the user ID
        
        # Creating admin user profile
        admin_profile = UserProfile(
            user_id=admin_user.id,
            plant_hardiness_zone="6b",
            zip_code="20001",
            city="Washington",
            state="DC"
        )
        db.session.add(admin_profile)
        
        # Committing all changes
        db.session.commit()
        
        print(f"Regular test user created with ID: {test_user.id}")
        print(f"Admin test user created with ID: {admin_user.id}")
        print("You can log in with:")
        print("- Regular user: username='gardener', password='GardenPassword123!'")
        print("- Admin user: username='admin', password='AdminPassword123!'")

if __name__ == "__main__":
    create_test_users()