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

## Date: 2/15/2025

## 12. **Fetching and Displaying Plant Data in the Frontend**

### **Purpose**

Today, we connected the frontend to the backend API to fetch and display real plant data. We previously had mock data, but now our frontend dynamically retrieves plant information from the database.

### **Steps Taken**

1. **Set Up API Call in the Frontend**

    - Created an API service (`api.ts`) to fetch plant data from `http://127.0.0.1:5000/api/plants/get_plants`.
    - Updated `Home.tsx` to use the `getPlants()` function with `useEffect()`.

2. **Fixed Backend API Connection Issues**

    - Encountered `ERR_CONNECTION_REFUSED` due to the backend not running.
    - Restarted Flask and ensured the frontend could communicate with `localhost:5000`.

3. **Implemented Styling Using CSS Modules**

    - Created `Home.module.css` for styling the Home page.
    - Applied styles to display plant data in readable, structured cards.

4. **Resolved Issues with API Response Formatting**
    - Previously, the API returned null values for some plant attributes.
    - Updated the backend to provide `"N/A"` or `false` defaults when needed.
    - Ensured JSON responses followed camelCase naming conventions.

### **Testing**

-   Successfully fetched live plant data from the database.
-   Displayed plant names and descriptions dynamically in the frontend.
-   Styled the list of plants for better readability.
-   Resolved API and CORS-related issues.

---

## 13. **User Authentication & Navbar Improvements**

### **Purpose**

We implemented **user authentication** in the frontend, allowing users to log in and log out while ensuring secure token storage. Additionally, we improved the **navbar styling** for better navigation.

### **Steps Taken**

1. **Implemented Login & Logout in the Frontend**

    - Created `Login.tsx` with a form for user authentication.
    - Integrated API calls to the backend for login.
    - Stored JWT token securely in `localStorage`.
    - Created an `AuthContext.tsx` to manage authentication state globally.
    - Ensured the navbar dynamically updates based on login status.

    **Testing:**

    - Successfully logged in with a test user.
    - Verified JWT token storage and persistence.
    - Implemented logout functionality that clears the token and updates UI.

2. **Fixed Issues with Protected Routes**

    - Wrapped protected pages in `ProtectedRoute.tsx` to restrict access.
    - Used `useContext(AuthContext)` to check authentication state before rendering.
    - Implemented redirect logic to send unauthorized users to the login page.

    **Testing:**

    - Verified that logged-out users cannot access the dashboard.
    - Ensured logged-in users can navigate protected routes.

3. **Styled the Navbar for Better UI**

    - Moved navigation links (`Home`, `Login`, `Logout`) into a **styled navbar**.
    - Applied **flexbox styling** to align navbar items properly.
    - Used CSS Modules (`Navbar.module.css`) for a cleaner UI.

    **Testing:**

    - Links are properly spaced and aligned.
    - The navbar updates dynamically when a user logs in or logs out.

---

## 14. **Next Steps**

-   Improve the **login UI/UX** with better form validation and feedback messages.
-   Implement **user registration** on the frontend.
-   Add a **"Remember Me"** option for persistent login.
-   Enhance error handling for API authentication failures.
-   Continue improving UI design and responsiveness.

---

This update completes user authentication in the frontend and improves navigation, bringing us closer to a fully interactive experience.

This update also marks the first time our frontend is successfully interacting with real data from the backend! 🚀

---

## Date: 2/16/2025

## 15. **Frontend Validation, Layout, and Styling Enhancements**

### **Purpose**

Today, we focused on improving the **user experience** by adding form validation, refining the layout, and enhancing the styling of the authentication pages. This ensures a **better, more professional UI** while preventing invalid user input.

### **Steps Taken**

1. **Improved Input Validation**

    - **Added frontend validation** in `Login.tsx` and `Register.tsx` to prevent empty submissions and enforce password length requirements.
    - Created a **`validateInputs` function** in `Login.tsx` to handle validation before sending requests to the backend.
    - Implemented **real-time validation feedback** by displaying error messages when fields are invalid.

2. **Refined Layout and Styling**

    - Updated **`Login.tsx` and `Register.tsx`** with a modern, nature-inspired styling theme.
    - Improved **form spacing and alignment** to enhance readability.
    - Added **disabled states for buttons** to prevent duplicate submissions when requests are processing.

3. **Moved API Base URL to Environment File**

    - Refactored `API_BASE_URL` across the frontend to use an **environment variable (`.env`)**.
    - Updated `.gitignore` to **prevent committing `.env` files** to the repository.

4. **Navbar Styling Enhancements**

    - Applied a **cohesive styling theme** to `Navbar.tsx` for a more **polished and professional** look.
    - Ensured navbar elements are **properly aligned and responsive** for different screen sizes.
    - Dynamically updated the **login/logout button visibility** based on authentication status.

    **Testing**

    - Verified that users cannot submit login or registration forms with invalid input.
    - Ensured **error messages** display correctly for missing fields and weak passwords.
    - Tested **successful user registration and login flows** with the new styling.
    - Confirmed that **the navbar updates dynamically** when users log in or out.
    - Validated that **environment variables are correctly used** to fetch the API base URL.

---

## 16. **Next Steps**

-   Implement **user session persistence** to keep users logged in across page refreshes.
-   Build the **protected dashboard route** to test authentication functionality.
-   Improve **error handling from the backend** to display more user-friendly messages.
-   Add additional UI refinements to **optimize responsiveness and mobile compatibility**.

---

Today's updates significantly improved the UI, making the authentication system more user-friendly and visually appealing.

---

## Date: 2/17/2025

## 17. **User Profile Setup, JWT Fixes, and API Improvements**

### **Purpose**

Today, we focused on enabling **user profile creation and retrieval** while resolving **JWT authentication issues** that caused profile fetch failures. We also improved frontend-backend consistency in data formatting and handling.

### **Steps Taken**

1. **Fixed JWT Subject Claim Issues**

    - Adjusted the **JWT token structure** to include `sub` as a string to align with `flask_jwt_extended`'s requirements.
    - Verified token validity using `curl` and ensured correct `Authorization: Bearer` header format.

2. **Implemented First-Time Profile Creation Support**

    - Previously, if a user had no existing profile, the frontend would fail to fetch data.
    - Now, an empty profile is returned (`{ "first_name": "", "last_name": "", "zip_code": "", "plant_hardiness_zone": "" }`) instead of failing with a `422 Unprocessable Entity`.
    - **Tested via frontend and `curl` to confirm expected behavior.**

3. **Standardized Data Format Between Frontend and Backend**

    - Updated `users.py` to correctly map frontend keys (`firstName`, `lastName`, `zipCode`) to database fields (`first_name`, `last_name`, `zip_code`).
    - Ensured consistent camelCase → snake_case conversions for API requests.

4. **Updated `Profile.tsx` to Handle First-Time Profile Creation**

    - Added logic to prevent failures when fetching an empty profile.
    - Handled missing data gracefully instead of showing undefined values.

5. **Improved Debug Logging for API Calls**

    - Added **debugging logs** to `users.py` to track incoming requests and responses.
    - Logged token usage and database queries for easier troubleshooting.

6. **Refactored `api.ts` for Improved Error Handling**
    - Updated `api.get()` and `api.post()` to provide **better error messages** in the console.
    - Ensured proper handling of API failures when fetching or updating profiles.

### **Testing**

-   Successfully **fetched and created user profiles** via **frontend and `curl`**.
-   **Confirmed JWT authentication fixes** by verifying proper token usage.
-   Ensured **profile creation logic works as expected** on first login.

---

## 18. **Next Steps**

-   Implement **frontend UI validation** for profile form fields.
-   Improve **error handling** for failed API requests with user-friendly messages.
-   Allow users to **update and save** additional profile details (e.g., garden preferences).
-   Add **unit tests** for backend API endpoints.

---

Today's changes fixed key issues with **JWT authentication, profile creation, and frontend-backend consistency**, ensuring a smoother user experience when setting up profiles for the first time.

---

This log serves as a detailed reference for backend and frontend setup, security improvements, and future development plans.
