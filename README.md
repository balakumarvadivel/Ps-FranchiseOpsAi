# FranchiseOps AI

AI-powered Franchise Operations Management System — React + Vite + Tailwind frontend,
FastAPI backend, PostgreSQL database.

## Build status

| Phase | Status |
|---|---|
| 1. Architecture | ✅ Done — see `docs/ARCHITECTURE.md` |
| 2. Database (schema + seed data) | ✅ Done — see `database/` |
| 3. Backend — Auth, Outlets, Sales, Inventory, AI Insights | ✅ Done — see `backend/` |
| 3. Backend — Staff, Marketing, Audit, Reports, Notifications routers | ⏳ Not yet built (same pattern as Outlets/Sales — see note in `backend/app/main.py`) |
| 4. Frontend (React dashboard) | ⏳ Not yet built in this repo (a standalone dummy-data version was built earlier as a single-file artifact) |
| 5–14 | ⏳ Not yet built |

This is being built incrementally, phase by phase, given the size of the full spec.

## Backend setup

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 14+ running locally (or a hosted instance, e.g. Render/Supabase)

### 2. Create the database
```bash
createdb franchiseops
psql -U postgres -d franchiseops -f database/schema.sql
psql -U postgres -d franchiseops -f database/seed.sql   # optional demo data
```

### 3. Install dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# edit .env — set DATABASE_URL and a real SECRET_KEY
```

### 5. Run the server
```bash
uvicorn app.main:app --reload --port 8000
```
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. Create your first user
Use the interactive docs (`/docs`) or curl:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Admin User","email":"admin@franchiseops.ai","password":"Admin@12345","role":"admin"}'
```
Copy the `access_token` from the response and use the "Authorize" button in
`/docs` (prefix with `Bearer `) to call protected endpoints.

## What's real vs. what's a placeholder right now

- **Real, working logic**: password hashing + JWT auth, role-based access control,
  outlet/sales/inventory CRUD, revenue forecasting (linear regression over actual
  `sales` rows), outlet health score (weighted composite over actual attendance,
  inventory, audit and sales data), rule-based recommendation engine, reorder and
  stock-transfer suggestions, executive summary generation — all computed from
  whatever is actually in your PostgreSQL database.
- **Placeholder / next phase**: Staff, Marketing, and Audit each have DB tables and
  models already, but dedicated routers/endpoints for them aren't built yet — they
  follow the exact same `router → service → model` pattern as `outlets.py` /
  `sales.py`, so extending is mostly copy-and-adapt. Reports (PDF/Excel/CSV
  generation) and the notifications/alerts feed are also not yet wired up.

## Repository layout
See `docs/ARCHITECTURE.md` for the full folder structure, system diagram, and
naming conventions.
