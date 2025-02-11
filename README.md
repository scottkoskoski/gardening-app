# Gardening App

## Overview

This project is a web application that provides users with personalized gardening recommendations based on their geographic location, climate zone, and local weather patterns. The application integrates real-time data to suggest what plants to grow and what gardening tasks to perform at any given time.

## Features

-   User Location Input: Users can enter their ZIP code or allow geolocation detection.
-   Climate Zone Identification: Determines the user's USDA Plant Hardiness Zone.
-   Weather Data Integration: Fetches current and forecasted weather data.
-   Planting Recommendations: Suggests suitable plants and optimal planting schedules.
-   Interactive Garden Planner (Future): Allows users to visualize and manage their garden layout.
-   User Accounts & Authentication (Upcoming): Users will be able to save their garden plans and receive personalized reminders.

## Tech Stack

-   Backend: Flask (Python), Flask-Migrate, Flask-SQLAlchemy
-   Frontend: React.js (To be implemented)
-   Database: SQLite (currently), PostgreSQL (planned for production)
-   APIs Used:
    -   [USDA Plant Hardiness Zone API](https://phzmapi.org/) – Determines planting zones by ZIP code.
    -   [Open-Meteo](https://open-meteo.com/) – Provides real-time weather data.
    -   [OpenFarm API](https://openfarm.cc/) – Fetches plant data (Pending API key setup).

## Project Structure

```
/gardening-app
│── backend/
│   │── app/
│   │   │── models/  # Database models
│   │   │── routes/  # API routes
│   │   └── __init__.py  # App factory
│   │── migrations/  # Database migrations
│   └── run.py  # Entry point
│── frontend/ (Coming Soon)
└── README.md
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repo-url>
cd gardening-app
```

### 2. Set Up the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Flask

```bash
export FLASK_APP=app  # Windows: $env:FLASK_APP = "app"
export FLASK_ENV=development  # Windows: $env:FLASK_ENV = "development"
```

### 4. Initialize the Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Run the Application

```bash
flask run
```

Server runs at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## API Endpoints

### Plant Hardiness Zone

-   GET `/api/hardiness/get_hardiness_zone?zip=<ZIP>`
-   Response: `{ "hardiness_zone": "7a" }`

### Weather Data

-   GET `/api/weather/get_weather?zip=<ZIP>`
-   Response: `{ "temperature": 65, "precipitation": 0 }`

### Plant Data

-   GET `/api/plants/get_plants`
-   Response: `{ "plants": [ { "name": "Tomato", "zone": "5-9" } ] }`

### User Registration

-   POST `/api/users/register`
-   Request Body: `{ "username": "testuser", "email": "test@example.com", "password": "mypassword" }`
-   Response: `{ "message": "User registered successfully." }`

## Future Enhancements

-   User Authentication & Login (JWT-based)
-   Garden Planning Tool with Drag-and-Drop UI
-   Notifications for Planting & Harvesting Schedules
-   Community Features: Connect Local Gardeners

## License

Currently, this project is private and does not have a public license.

---

Next Steps: Set up authentication for user login.
