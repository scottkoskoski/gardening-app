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

## 6. **User Registration Endpoint**

### Purpose

Allows users to create an account with a **username, email, and password**.

### Steps Taken

-   Created `users.py` inside `app/routes/`.
-   Used **Flask-SQLAlchemy** to manage users.
-   Hashed passwords before storing them.
-   Registered the blueprint for `/api/users`.

**Tested using:**

```bash
curl -X POST http://127.0.0.1:5000/api/users/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "mypassword"}'
```

Expected output:

```json
{ "message": "User registered successfully.", "user_id": 1 }
```

---

## 7. **Fixing Issues & Debugging**

During development, we encountered and fixed the following issues:

1. **Module Import Errors**: Fixed issues related to Python path settings and module imports.
2. **Database Table Not Found**: Ensured proper migration steps and confirmed `flask db upgrade` ran successfully.
3. **Flask-Migrate Not Recognized**: Added correct `import` statements in `__init__.py`.
4. **Incorrect API Requests**: Debugged malformed curl requests.

---

## Summary & Next Steps

### What We Accomplished Today:

-   Successfully initialized the Flask project and set up virtual environments.
-   Created and tested the **Hardiness Zone API**.
-   Created and tested the **Weather API**.
-   Set up an **SQLite database** and implemented Flask-Migrate.
-   Developed and tested **User Registration**.
-   Fixed several common web development errors.

### Next Steps:

-   Implement **User Authentication** (JWT-based login/logout).
-   Finalize the **Plant Data API** (integrate OpenFarm API).
-   Plan the **Frontend Implementation** (React setup).

---

This log should serve as a useful tutorial for anyone starting with **Flask, APIs, and databases**. Let me know if anything needs clarification or updating.
