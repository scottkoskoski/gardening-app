# Gardening App

## Overview

This project is a web application that provides users with personalized gardening recommendations based on their geographic location, climate zone, and local weather patterns. The application integrates real-time data to suggest what plants to grow and what gardening tasks to perform at any given time.

## Features

-   **User Location Input**: Users can enter their ZIP code or allow geolocation detection.
-   **Climate Zone Identification**: Determines the user's USDA Plant Hardiness Zone.
-   **Weather Data Integration**: Fetches current and forecasted weather data.
-   **Planting Recommendations**: Suggests suitable plants and optimal planting schedules.
-   **Database of Plants**: Stores plant data fetched from OpenFarm API.
-   **User Accounts & Authentication**: Users can register, log in, and receive personalized recommendations.
-   **JWT-Based Authentication**: Secure user authentication using JSON Web Tokens.
-   **React Frontend with TypeScript**: A modern UI built using React.js with TypeScript for type safety.
-   **Vite for Fast Development**: Uses Vite for efficient frontend bundling and development.
-   **Protected Routes**: Certain pages require authentication before access is granted.
-   **Navigation Bar**: Provides dynamic navigation based on authentication state.

## Tech Stack

-   **Backend**: Flask (Python), Flask-Migrate, Flask-SQLAlchemy, Flask-JWT-Extended
-   **Frontend**: React.js with TypeScript, Vite, React Router
-   **Database**: SQLite (currently), PostgreSQL (planned for production)
-   **APIs Used**:
    -   [USDA Plant Hardiness Zone API](https://phzmapi.org/) – Determines planting zones by ZIP code.
    -   [Open-Meteo](https://open-meteo.com/) – Provides real-time weather data.
    -   [OpenFarm API](https://openfarm.cc/) – Fetches plant data.

## Project Structure

```
/gardening-app
│── backend/
│   │── app/
│   │   │── models/  # Database models
│   │   │── routes/  # API routes
│   │   └── __init__.py  # App factory
│   │── instance/  # SQLite database storage
│   │── migrations/  # Database migrations
│   │── scripts/  # Utility scripts
│   │   └── fetch_openfarm_data.py  # Script to populate the database with plant data
│   └── run.py  # Entry point
│── frontend/
│   │── src/  # React source code
│   │   │── components/  # Reusable UI components
│   │   │── pages/  # Page components
│   │   │── services/  # API service calls
│   │   │── styles/  # Styling (CSS Modules)
│   │── public/  # Static assets
│   │── .gitignore  # Ignores node_modules and build files
│   │── package.json  # Project dependencies
│   │── tsconfig.json  # TypeScript configuration
│   └── vite.config.ts  # Vite configuration
│── README.md
```

## Setup Instructions

### **1. Clone the Repository**

```bash
git clone <repo-url>
cd gardening-app
```

---

## **Setting Up the Backend**

### **2. Set Up the Backend Environment**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **3. Configure Flask**

```bash
export FLASK_APP=app  # Windows: $env:FLASK_APP = "app"
export FLASK_ENV=development  # Windows: $env:FLASK_ENV = "development"
```

### **4. Initialize the Database**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### **5. Fetch Plant Data from OpenFarm API**

```bash
python scripts/fetch_openfarm_data.py
```

### **6. Run the Backend**

```bash
flask run
```

The backend should now be running at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## **Setting Up the Frontend**

### **1. Install Dependencies**

```bash
cd frontend
npm install
```

### **2. Run the Frontend**

```bash
npm run dev
```

The frontend should now be running at: [http://localhost:5173](http://localhost:5173)

---

## Untracked Files

Certain files are required but are **not tracked** in Git for security reasons. You may need to create them manually:

-   **backend/.env** – Contains environment variables, such as:
    ```
    SECRET_KEY=<your_secret_key>
    ```
-   **frontend/.env** – If API keys or environment settings are required for the frontend.

Ensure these files exist before running the project.

---

## API Endpoints

### **Plant Hardiness Zone**

-   **GET** `/api/hardiness/get_hardiness_zone?zip=<ZIP>`
-   **Response:**
    ```json
    { "hardiness_zone": "7a" }
    ```

### **Weather Data**

-   **GET** `/api/weather/get_weather?zip=<ZIP>`
-   **Response:**
    ```json
    { "temperature": 65, "precipitation": 0 }
    ```

### **Plant Data**

-   **GET** `/api/plants/get_plants`
-   **Response:**
    ```json
    { "plants": [{ "name": "Tomato", "zone": "5-9" }] }
    ```

### **User Registration**

-   **POST** `/api/users/register`
-   **Request Body:**
    ```json
    {
        "username": "testuser",
        "email": "test@example.com",
        "password": "mypassword"
    }
    ```
-   **Response:**
    ```json
    { "message": "User registered successfully.", "user_id": 1 }
    ```

### **User Login**

-   **POST** `/api/users/login`
-   **Request Body:**
    ```json
    { "email": "test@example.com", "password": "mypassword" }
    ```
-   **Response:**
    ```json
    { "message": "Login successful!", "token": "<JWT_TOKEN>" }
    ```

### **Get User Information (JWT Required)**

-   **GET** `/api/users/get_user`
-   **Headers:**
    ```http
    Authorization: Bearer <JWT_TOKEN>
    ```
-   **Response:**
    ```json
    { "id": 1, "username": "testuser", "email": "test@example.com" }
    ```

---

## Future Enhancements

-   **User Registration Page** – Allow users to create new accounts from the frontend.
-   **User Dashboard** – Display personalized gardening recommendations.
-   **Session Management** – Improve JWT handling and refresh tokens.
-   **UI Improvements** – Enhance responsiveness and design.

## Next Steps

-   Implement user registration in the frontend.
-   Improve the authentication UI with better error handling and form validation.
-   Implement logout functionality with state updates.
