# Project Log - Gardening App

## Date: 2/10/2025

This document serves as a detailed log of today's work on the **Gardening App** backend. The goal is to provide a step-by-step breakdown that is useful for someone who is new to web development.

---

## 1. **Project Initialization**

### Setting Up the Project Structure

We started by ensuring that the project follows a clean and organized structure. The project root contains both the `backend` and `frontend` directories, with all backend code inside `backend/`.

```
/gardening-app
│── backend/
│   │── app/
│   │   │── models/  # Database models
│   │   │── routes/  # API routes
│   │   └── __init__.py  # App factory
│   │── migrations/  # Database migrations
│   │── instance/  # SQLite database storage
│   │── scripts/  # Scripts for data fetching
│   └── run.py  # Entry point
│── frontend/ (Coming Soon)
└── README.md
```

### Setting Up a Virtual Environment

To ensure all dependencies are properly installed in an isolated environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. **Setting Up Flask**

We configured Flask to recognize the project and allow us to run the server:

```bash
export FLASK_APP=app  # Windows: $env:FLASK_APP = "app"
export FLASK_ENV=development  # Enables debug mode
```

To verify the setup:

```bash
flask run
```

This should start the server at `http://127.0.0.1:5000`.

---

## 3. **Implementing the Hardiness Zone API**

### Purpose

The **Hardiness Zone API** helps users determine the appropriate USDA planting zone based on their ZIP code.

### Steps Taken

-   Created `hardiness.py` inside `app/routes/`.
-   Integrated with `phzmapi.org` to fetch the correct hardiness zone.
-   Registered a Flask blueprint for API routing.

**Tested using:**

```bash
curl http://127.0.0.1:5000/api/hardiness/get_hardiness_zone?zip=10001
```

Expected output:

```json
{ "hardiness_zone": "7a" }
```

---

## 4. **Implementing the Weather API**

### Purpose

The **Weather API** fetches real-time weather data based on the user's location.

### Steps Taken

-   Created `weather.py` inside `app/routes/`.
-   Integrated with **Open-Meteo** for weather forecasts.
-   Registered a Flask blueprint.

**Tested using:**

```bash
curl http://127.0.0.1:5000/api/weather/get_weather?zip=10001
```

Expected output:

```json
{ "temperature": 65, "precipitation": 0 }
```

---

## 5. **Setting Up the Database**

### Initial Database Setup

We used **Flask-SQLAlchemy** for ORM and **Flask-Migrate** for database migrations.

**Key Steps:**

1. Defined `models/database.py` to initialize SQLAlchemy.
2. Created `models/plant.py` and `models/user.py` for data tables.
3. Ran the following commands:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 6. **User Registration & Authentication**

### Purpose

Allows users to register and log in using JWT-based authentication.

### Steps Taken

-   Created `users.py` inside `app/routes/`.
-   Implemented **password hashing** and **JWT token-based authentication**.
-   Registered a Flask blueprint for `/api/users`.

**User Registration**

```bash
curl -X POST http://127.0.0.1:5000/api/users/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "mypassword"}'
```

Expected output:

```json
{ "message": "User registered successfully.", "user_id": 1 }
```

**User Login**

```bash
curl -X POST http://127.0.0.1:5000/api/users/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "mypassword"}'
```

Expected output:

```json
{ "message": "Login successful!", "token": "<JWT_TOKEN>" }
```

---

## Date: 2/13/2025

## 7. **Fetching Plant Data from OpenFarm API**

### Purpose

We integrated OpenFarm's API to fetch and store plant data in our database.

### Steps Taken:

-   Implemented `fetch_openfarm_data.py` in `scripts/` to query OpenFarm for plant data.
-   Stored relevant attributes (name, sunlight, sowing method, spacing, height, description, and image URL).
-   Avoided duplicate entries by checking for existing plants before insertion.
-   Verified that data was correctly inserted into the `plant` table.

### Database Verification:

To confirm the data was stored successfully, we ran:

```bash
sqlite3 instance/gardening.db
SELECT * FROM plant LIMIT 5;
```

Example output:

```txt
1|Tomato||||||0|0|||Full Sun||Direct seed indoors, transplant seedlings outside after hardening off|45.0|45.0|45.0|The tomato is the fruit of the tomato plant, a member of the Nightshade family (Solanaceae).|https://s3.amazonaws.com/openfarm-project/production/media/pictures/attachments/5dc3618ef2c1020004f936e4.jpg?1573085580
```

---

## 8. **Summary & Next Steps**

### What We Accomplished Today:

-   Implemented **user authentication and JWT-based login**.
-   Successfully fetched and stored plant data from the OpenFarm API.
-   Verified data insertion in SQLite and confirmed plant records exist in the `plant` table.

### Next Steps:

-   Build API endpoints to query plant data efficiently.
-   Set up the **frontend structure** for integrating with the backend.
-   Implement user profile management and authentication improvements.

---

This log serves as a useful reference for managing database migrations, API data fetching, and Flask application setup.
