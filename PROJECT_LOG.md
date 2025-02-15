# Project Log - Gardening App

## Date: 2/10/2025

This document serves as a detailed log of today's work on the **Gardening App** backend. The goal is to provide a step-by-step breakdown that is useful for someone who is new to web development.

---

## 1. **Project Initialization**

### Setting Up the Project Structure

We started by ensuring that the project follows a clean and organized structure. The project root contains both the backend and frontend directories, with all backend code inside backend/.

/gardening-app
│── backend/
│ │── app/
│ │ │── models/ # Database models
│ │ │── routes/ # API routes
│ │ └── **init**.py # App factory
│ │── migrations/ # Database migrations
│ │── instance/ # SQLite database storage
│ │── scripts/ # Scripts for data fetching
│ └── run.py # Entry point
│── frontend/ (Coming Soon)
└── README.md

### Setting Up a Virtual Environment

To ensure all dependencies are properly installed in an isolated environment:

bash
cd backend
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt

---

## 2. **Setting Up Flask**

We configured Flask to recognize the project and allow us to run the server:

bash
export FLASK_APP=app # Windows: $env:FLASK_APP = "app"
export FLASK_ENV=development # Enables debug mode

To verify the setup:

bash
flask run

This should start the server at http://127.0.0.1:5000.

---

## 3. **Implementing the Hardiness Zone API**

### Purpose

The **Hardiness Zone API** helps users determine the appropriate USDA planting zone based on their ZIP code.

### Steps Taken

-   Created hardiness.py inside app/routes/.
-   Integrated with phzmapi.org to fetch the correct hardiness zone.
-   Registered a Flask blueprint for API routing.

**Tested using:**

bash
curl http://127.0.0.1:5000/api/hardiness/get_hardiness_zone?zip=10001

Expected output:

json
{ "hardiness_zone": "7a" }

---

## 4. **Implementing the Weather API**

### Purpose

The **Weather API** fetches real-time weather data based on the user's location.

### Steps Taken

-   Created weather.py inside app/routes/.
-   Integrated with **Open-Meteo** for weather forecasts.
-   Registered a Flask blueprint.

**Tested using:**

bash
curl http://127.0.0.1:5000/api/weather/get_weather?zip=10001

Expected output:

json
{ "temperature": 65, "precipitation": 0 }

---

## 5. **Setting Up the Database**

### Initial Database Setup

We used **Flask-SQLAlchemy** for ORM and **Flask-Migrate** for database migrations.

**Key Steps:**

1. Defined models/database.py to initialize SQLAlchemy.
2. Created models/plant.py and models/user.py for data tables.
3. Ran the following commands:

bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

---

## 6. **User Registration & Authentication**

### Purpose

Allows users to register and log in using JWT-based authentication.

### Steps Taken

-   Created users.py inside app/routes/.
-   Implemented **password hashing** and **JWT token-based authentication**.
-   Registered a Flask blueprint for /api/users.

**User Registration**

bash
curl -X POST http://127.0.0.1:5000/api/users/register \
 -H "Content-Type: application/json" \
 -d '{"username": "testuser", "email": "test@example.com", "password": "mypassword"}'

Expected output:

json
{ "message": "User registered successfully.", "user_id": 1 }

**User Login**

bash
curl -X POST http://127.0.0.1:5000/api/users/login \
 -H "Content-Type: application/json" \
 -d '{"email": "test@example.com", "password": "mypassword"}'

Expected output:

json
{ "message": "Login successful!", "token": "<JWT_TOKEN>" }

---

## Date: 2/13/2025

## 7. **Frontend Initialization with React and TypeScript**

### Purpose

We initialized the frontend using React with TypeScript and Vite for a modern, performant setup.

### Steps Taken:

1. Created the frontend project:

bash
cd gardening-app
npm create vite@latest frontend --template react-ts

2. Installed dependencies:

bash
cd frontend
npm install

3. Ran the development server:

bash
npm run dev

The frontend is now running at http://localhost:5173/.

---

## 8. **Securing the User API with JWT Authentication**

### Purpose

Previously, get_user() allowed users to fetch data using an email query, which was insecure. We improved security by requiring a JWT token for authentication.

### Steps Taken:

-   Updated users.py to require a **Bearer token** in the request headers.
-   Implemented JWT decoding and validation.
-   Prevented unauthorized access to user data.

**Testing Secure Requests:**

bash
curl -X GET http://127.0.0.1:5000/api/users/get_user \
 -H "Authorization: Bearer <JWT_TOKEN>"

Expected output:

json
{ "id": 1, "username": "testuser", "email": "test@example.com" }

---

## 9. **Next Steps**

-   Implement authentication UI in the frontend.
-   Connect the frontend to the backend API.
-   Build user registration and login pages.
-   Store JWT tokens securely in the frontend.

---

## Date: 2/14/2025

## 10. **Setting Up React Router**

### Purpose

To enable navigation between different pages in the frontend, we set up **React Router**. This allows us to create multiple views (such as Home and Login) while keeping the application in a single-page format.

### Steps Taken:

1. **Installed React Router**:

    ```bash
    cd frontend
    npm install react-router-dom
    ```

2. **Created a `routes.tsx` file in `src/`**:

    - This file defines different routes for the app.

    ```tsx
    import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
    import Home from "./pages/Home";
    import Login from "./pages/Login";

    const AppRoutes = () => (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
            </Routes>
        </Router>
    );

    export default AppRoutes;
    ```

3. **Created a `pages/` directory inside `src/` and added `Home.tsx` and `Login.tsx`**:

    - **Home.tsx**

    ```tsx
    const Home = () => {
        return <h1>Welcome to the Gardening App!</h1>;
    };

    export default Home;
    ```

    - **Login.tsx**

    ```tsx
    const Login = () => {
        return <h1>Login Page</h1>;
    };

    export default Login;
    ```

4. **Updated `App.tsx` to use the new routing system**:

    ```tsx
    import AppRoutes from "./routes";

    function App() {
        return <AppRoutes />;
    }

    export default App;
    ```

5. **Ran the development server to test navigation**:
    ```bash
    npm run dev
    ```
    - Visiting `http://localhost:5173/` showed the Home page.
    - Visiting `http://localhost:5173/login` showed the Login page.

### Key Takeaways

-   **React Router** allows us to create a **multi-page app without full-page reloads**.
-   Navigation between pages is now dynamic and controlled via JavaScript.
-   The `pages/` directory organizes our different screens, making the project more maintainable.

---

## 11. **Next Steps**

-   Build a user authentication form in the frontend.
-   Connect the frontend login page to the backend API.
-   Store JWT tokens securely in local storage or cookies.

---

This log continues to serve as a detailed reference for backend and frontend setup, security improvements, and future development plans.

---

This log serves as a detailed reference for backend and frontend setup, security improvements, and future development plans.
