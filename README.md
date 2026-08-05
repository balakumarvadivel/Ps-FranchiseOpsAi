# FranchiseOps AI

AI-powered Franchise Operations Management System — React + Vite + Tailwind frontend,
FastAPI backend, PostgreSQL database.

## Build status

| Phase | Status |
|---|---|
| 1. Architecture | ✅ Done — see `docs/ARCHITECTURE.md` |
| 2. Database (schema + seed data) | ✅ Done — see `database/` |
| 3. Backend — Auth, Outlets, Sales, Inventory, Staff, Marketing, Audit, AI Insights, Recommendations, Alerts, Notifications, Reports | ✅ Done — see `backend/` |
| 4. Frontend — React + Vite + Tailwind, wired to every backend endpoint above (no dummy data) | ✅ Done — see `frontend/` |
| 5. Data Validation & Processing — CSV/Excel upload, cleaning, data quality score | ✅ Done — `/app/data-validation` in the frontend, `services/data_validation.py` in the backend |
| Alert scan scheduling | ✅ Done — runs automatically every 15 min via APScheduler (`services/scheduler.py`) |
| Recommendation refresh scheduling | ⏳ Manual only (`POST /recommendations/refresh`) — intentionally not auto-scheduled since it clears open recommendations first |
| 6–14 (remaining spec items) | Mostly already covered by what's built — see the module table below |

This is being built incrementally, phase by phase, given the size of the full spec.


## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env      # only needed if backend is on a different origin
npm run dev
```
Opens at http://localhost:5173. Requests to `/api/*` are proxied to the backend
at `http://localhost:8000` by `vite.config.js` — make sure the backend is
running first (see below), and that you've registered a user via `/register`.

Every page — Dashboard, Outlet/Inventory/Staff/Marketing/Audit Agents,
Intelligence Engine, Recommendations, Reports, Settings — calls the live
FastAPI endpoints via React Query; there is no dummy/mock data in this build.
I verified every relative import resolves, every named/default import matches
a real export, and all 59 frontend API calls match an actual backend route —
but I couldn't run `npm install`/`vite build` in this sandbox (no network
access), so a first real build may still surface something a static check
can't catch (e.g. a JSX typo) — if so, paste the error back and I'll fix it.


## What each backend module covers

| Module | Router | Key AI feature(s) |
|---|---|---|
| Auth | `/api/v1/auth` | JWT, RBAC (admin / regional_manager / outlet_manager), forgot/reset password |
| Outlets | `/api/v1/outlets` | Outlet ranking with revenue, growth %, health score |
| Sales | `/api/v1/sales` | Daily/Weekly/Monthly/Yearly trend aggregation |
| Inventory | `/api/v1/inventory` | Reorder recommendations, outlet-to-outlet transfer suggestions |
| Staff | `/api/v1/staff` | Performance score, attrition risk, best employee, shift optimization |
| Marketing | `/api/v1/marketing` | Campaign ROI ranking, customer segmentation, budget optimization |
| Audit | `/api/v1/audits` | Risk score, fraud-risk flag, compliance recommendation |
| AI Insights | `/api/v1/ai` | Revenue forecasting (regression), outlet health breakdown, executive summary (NLG) |
| Recommendations | `/api/v1/recommendations` | Persisted, prioritized business recommendations, refreshable on demand |
| Alerts & Notifications | `/api/v1/alerts`, `/api/v1/notifications` | Auto-generated alerts (low stock, expiring stock, poor performance, staff shortage, audit due, campaign ending) |
| Reports | `/api/v1/reports` | PDF / Excel / CSV generation for every domain, downloadable |
| Data Validation | `/api/v1/data-validation` | CSV/Excel upload, missing/duplicate/invalid-value detection, data quality score, cleaning suggestions, commit-to-DB |


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
  full CRUD across outlets/sales/inventory/staff/marketing/audits, revenue
  forecasting (linear regression over actual `sales` rows), outlet health score
  (weighted composite over actual attendance, inventory, audit and sales data),
  employee performance score + rule-based attrition risk, campaign ROI ranking,
  rule-based customer segmentation, audit risk/fraud scoring, a rule-based
  recommendation engine (persisted + refreshable), an alert scanner that inspects
  live data and creates alerts, and PDF/Excel/CSV report generation — all computed
  from whatever is actually in your PostgreSQL database, nothing hardcoded.
- **Not yet built**: the React frontend for this backend (Phase 4), the Data
  Validation & Processing CSV/Excel upload module (Phase 5), and the alert scan /
  recommendation refresh are currently manually triggered via API rather than run
  on a schedule (wire up a cron job or APScheduler for that in production).

## Repository layout
See `docs/ARCHITECTURE.md` for the full folder structure, system diagram, and
naming conventions.
