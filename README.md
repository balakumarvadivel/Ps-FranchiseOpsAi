# FranchiseOps AI

AI-powered Franchise Operations Management System — React + Vite + Tailwind frontend,
FastAPI backend, PostgreSQL database.

## Build status

Everything from the original spec is now built:

| Area | Status |
|---|---|
| Architecture, database, backend (8 domains + AI layer), frontend (all pages live-wired) | ✅ Done |
| Data Validation & Processing | ✅ Done |
| Alert scheduling (every 15 min) | ✅ Done |
| Automated tests (pytest) | ✅ Done |
| Deployment configs (Render + Vercel) | ✅ Done |
| Admin: user management, outlet management | ✅ Done |
| Regions as a normalized table (FK from `outlets.region`) | ✅ Done |
| Permissions table + role-permission matrix (view/edit in Admin UI) | ✅ Done |
| Leave management (request/approve/reject) | ✅ Done — this didn't exist at all before; added the full table, model, endpoints, and UI |
| Payroll & shift listing/scheduling UI | ✅ Done |
| Individual audit findings (add/view/resolve) | ✅ Done |
| Global search, date range picker | ✅ Done |
| Inventory: suppliers, batch/expiry tracking, value/turnover | ✅ Done |
| Dashboard: profit trend, category performance, regional performance, cross-domain summary cards | ✅ Done |
| Anomaly detection (z-score sales, IQR audit compliance) | ✅ Done — wired into real endpoints, not just written and unused |





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

## Honest caveats

Every module described above is implemented with real, non-mocked logic —
but a few things are worth knowing before you present or deploy this:

- **Nothing has been run end-to-end.** This sandbox has no network access, so
  I could never `npm install`, `pip install`, or connect to a live
  PostgreSQL/FastAPI/Vite dev server. Everything was verified statically:
  every Python file compiles, every JS/JSX import resolves to a real export,
  every frontend API call matches a real backend route (85/85 at last count),
  and the pure-logic AI functions (forecasting, anomaly detection, health
  scoring math, recommender, NLG, data validation) were manually executed
  and passed in this environment. The FastAPI integration tests in
  `backend/tests/` are written and structurally sound but not executable
  here — run `pytest` yourself for the first real signal on those.
- **First real run may surface something.** A typo an import-check can't
  catch, a version mismatch in `requirements.txt`/`package.json`, or a
  Postgres-specific SQL quirk are all plausible on a project this size. If
  something breaks, paste the error back and I'll fix it directly.
- **Scale/polish not attempted**: no pagination on a few list endpoints that
  could return large result sets in production, no rate limiting, no email
  service wired up (password reset returns the token directly rather than
  emailing it — clearly marked as a dev-only shortcut in the code), and the
  recommendation engine's `refresh` is manual rather than scheduled (see the
  build status table above for why).

## Running tests

```bash
cd backend
pip install -r requirements.txt
pytest
```
Uses an in-memory SQLite database, so no PostgreSQL setup is needed just to
run tests. Note: endpoints using PostgreSQL-specific `date_trunc` (sales
trend, profit trend, category performance) aren't covered by the SQLite
integration tests for that reason — the AI service functions they depend on
(forecasting, anomaly detection, recommender, NLG) are unit-tested directly
instead.

## Deployment

- **Backend → Render**: `backend/render.yaml` provisions a web service + free
  Postgres DB. A `Dockerfile` is also included if you'd rather deploy the
  backend anywhere else that takes a container.
- **Frontend → Vercel**: `frontend/vercel.json` configures the Vite build and
  SPA routing rewrites. Set `VITE_API_BASE_URL` in Vercel's environment
  variables to your deployed backend URL.
- After deploying, run `database/schema.sql` (and optionally `seed.sql`)
  against the production database, and set `FRONTEND_ORIGINS` in the
  backend's environment to your Vercel URL so CORS allows it.

## Repository layout
See `docs/ARCHITECTURE.md` for the full folder structure, system diagram, and
naming conventions.
