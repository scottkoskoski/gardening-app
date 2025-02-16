# Gardening App

## Overview

The Gardening App is a full-stack web application that provides users with personalized gardening recommendations based on their geographic location, climate zone, and local weather patterns. Users can register, log in, and receive data-driven insights into optimal planting schedules and plant care.

## Features

-   **User Authentication**: Secure JWT-based authentication system.
-   **Location-Based Recommendations**: Determines USDA Plant Hardiness Zone based on ZIP code.
-   **Weather Integration**: Fetches real-time weather data using Open-Meteo API.
-   **Plant Database**: Stores plant data from OpenFarm API.
-   **Personalized Gardening Insights**: Users receive suggestions based on climate, season, and space constraints.
-   **React Frontend with TypeScript**: A modern UI for an intuitive user experience.
-   **Protected Routes**: Certain pages require authentication before access is granted.
-   **Dynamic Navigation**: Navbar updates based on user login status.

## Tech Stack

### Backend

-   **Flask** (Python)
-   **Flask-SQLAlchemy** (ORM)
-   **Flask-Migrate** (Database migrations)
-   **Flask-JWT-Extended** (Authentication)

### Frontend

-   **React.js with TypeScript**
-   **React Router** (Client-side navigation)
-   **Vite** (Fast frontend development)
-   **CSS Modules** (Scoped styling)

### Database

-   **SQLite** (Development database)
-   **PostgreSQL** (Planned for production)

### APIs Used

-   **[USDA Plant Hardiness Zone API](https://phzmapi.org/)** – Determines planting zones.
-   **[Open-Meteo](https://open-meteo.com/)** – Provides weather data.
-   **[OpenFarm API](https://openfarm.cc/)** – Fetches plant information.

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
│   │   └── fetch_openfarm_data.py  # Script to populate the database
│   └── run.py  # Entry point
│── frontend/
│   │── src/  # React source code
│   │   │── components/  # Reusable UI components
│   │   │── pages/  # Page components
│   │   │── services/  # API service calls
│   │   │── styles/  # CSS Modules
│   │── public/  # Static assets
│   │── .env  # Environment variables, including VITE_API_BASE_URL
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

### **2. Configure Environment Variables**

Create a `.env` file inside `frontend/` and define the API base URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

### **3. Run the Frontend**

```bash
npm run dev
```

The frontend should now be running at: [http://localhost:5173](http://localhost:5173)

---

## Future Enhancements

-   **User Dashboard** – Display personalized gardening recommendations.
-   **Session Management** – Improve JWT handling.
-   **Improved UI/UX** – Enhance responsiveness and accessibility.
-   **Additional APIs** – Integrate more data sources for advanced recommendations.
-   **Improve form validation and user feedback** – Enhance error handling and provide better UI feedback for login and registration.

## Next Steps

-   Implement logout with session management.
-   Continue improving UI and state management.

This updated `README.md` reflects the current state of the Gardening App and outlines future development goals.
