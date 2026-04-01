# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack gardening app providing personalized recommendations based on location, USDA hardiness zone, and weather. Flask backend + React/TypeScript frontend with JWT auth.

## Commands

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app
export FLASK_ENV=development
flask run                          # Runs on http://127.0.0.1:5000
flask db migrate -m "description"  # Create migration
flask db upgrade                   # Apply migrations
python app/scripts/fetch_openfarm_data.py  # Populate plant data from OpenFarm API
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # Dev server on http://localhost:5173
npm run build    # TypeScript check + Vite build
npm run lint     # ESLint
```

## Architecture

### Backend (Flask)
- **Entry point**: `backend/run.py` calls `create_app()` factory in `backend/app/__init__.py`
- **Database**: SQLite via Flask-SQLAlchemy, stored at `backend/instance/gardening.db`. Migrations managed with Flask-Migrate/Alembic in `backend/migrations/`
- **Auth**: JWT tokens via `flask_jwt_extended` + manual `PyJWT` encoding in login route. Tokens sent as `Authorization: Bearer <token>` headers. `admin_required()` decorator in `backend/app/routes/users.py` for admin-only routes.
- **Models** (`backend/app/models/`): `User`, `UserProfile`, `Plant`, `UserGarden`, `UserGardenPlant`, `GardenType`. All share a single `db` instance from `database.py`.
- **Routes** (`backend/app/routes/`): All registered as blueprints with `/api/` prefix. Key endpoints:
  - `/api/users/` - login, register, profile, get_user, inactive_users
  - `/api/plants/` - plant data from OpenFarm
  - `/api/hardiness/` - USDA hardiness zone lookup by ZIP
  - `/api/weather/` - weather via Open-Meteo
  - `/api/user_gardens/`, `/api/user_garden_plants/` - user garden CRUD
  - `/api/garden_types` - garden type reference data
- **Config**: Uses `python-dotenv`; expects `SECRET_KEY` in environment.

### Frontend (React + TypeScript + Vite)
- **API layer**: `frontend/src/services/api.ts` - all backend calls go through `get()`, `post()`, `deleteRequest()` helpers that prepend `API_BASE_URL/api`. Set `VITE_API_BASE_URL` in `frontend/.env`.
- **Auth**: `AuthContext` (`frontend/src/context/AuthContext.tsx`) stores JWT in localStorage, exposes `useAuth()` hook. `ProtectedRoute` component gates authenticated pages.
- **Routing**: `frontend/src/routes.tsx` - public routes (`/`, `/login`, `/register`) and protected routes (`/profile`, `/gardens`, `/dashboard`).
- **Pages**: Home, Login, Register, Profile, GardenView in `frontend/src/pages/`.

### Key Patterns
- Backend uses Marshmallow schemas (e.g., `UserSchema`) for serialization
- CORS configured for `http://localhost:5173` only
- Garden types use an enum (`GardenType`) for type safety
- Plant growth stages tracked via `GrowthStage` enum
