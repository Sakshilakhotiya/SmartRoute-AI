# SmartRoute AI — Smart Logistics & Route Intelligence Platform

A multi-service B.Tech project starter with a React + TypeScript frontend, Express + SQLite API, and FastAPI optimization service. It uses real OpenStreetMap Nominatim geocoding, OSRM road routing, and Open-Meteo weather when available. Estimates and unavailable data are labelled transparently.

## Architecture
- `frontend/`: React, Vite, TypeScript, Tailwind, Leaflet, Recharts, Framer Motion.
- `backend/`: Express REST API, JWT auth, bcrypt password hashing, SQLite persistence via better-sqlite3.
- `ai-service/`: FastAPI route scoring, cost estimation, vehicle suitability, weather context, and documented ML training workflow.

## Requirements
Node.js 20+, npm, Python 3.10+. Internet is needed for external map/geocoding/weather services. No paid API key is required for the basic demo. Public providers can rate-limit requests; use responsibly.

## Run locally (three terminals)
### 1) AI service
```bash
cd ai-service
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```
### 2) Backend API
```bash
cd backend
cp .env.example .env   # Windows: copy .env.example .env
npm install
npm run dev
```
The SQLite database is created automatically at `backend/data/smartroute.sqlite`.
### 3) Frontend
```bash
cd frontend
cp .env.example .env   # Windows: copy .env.example .env
npm install
npm run dev
```
Open the Vite URL printed in the terminal (normally http://localhost:5173).

## Useful API endpoints
- `GET /api/health`
- `POST /api/auth/register` `{ "name":"Demo User", "email":"demo@example.com", "password":"Password123!" }`
- `POST /api/auth/login`
- `GET /api/auth/me` (Bearer token)
- `POST /api/routes/plan` (Bearer token): geocodes locations, retrieves OSRM alternatives, asks AI service to rank them, and stores a planning-history record.
- `GET /api/routes/saved`, `POST /api/routes/saved`, `GET /api/routes/saved/:id`, `DELETE /api/routes/saved/:id`
- `GET /api/dashboard/summary`, `GET /api/analytics`
- AI service: `GET http://localhost:8001/health`, `POST /optimize/score`

## Honest data limitations
- OSRM public demo routing does not provide reliable live traffic. Travel times are routing-provider estimates, not live traffic predictions.
- Public Nominatim has usage policies and rate limits. Avoid bulk requests; configure a compatible provider via environment variables if needed.
- Weather is contextual destination weather from Open-Meteo, not road-level weather.
- Accessibility and risk scores are explicitly heuristic when reliable road attributes or incident data are absent; they are not verified safety guarantees.
- No ML model is claimed to be trained. `ai-service/app/ml_training.py` provides a reproducible import/train/evaluate workflow for a genuine dataset; MAE/RMSE are reported only after running it with your dataset.
- Analytics are derived from actual saved planning records and show empty states when there is no data.

## Tests
```bash
cd backend && npm install && npm test
cd ../ai-service && pip install -r requirements.txt && pytest
```
The included tests cover core scoring, input validation, and API health. Run them locally; this package does not claim tests have already passed in your environment.

## Security notes for a student project
Use a strong `JWT_SECRET` in `.env`, keep `.env` private, and do not use the development secret in production. Rate limiting and ownership checks are enabled. This is a demonstration baseline and should receive a security review before real deployment.
