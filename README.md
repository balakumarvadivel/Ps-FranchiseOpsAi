# FranchiseOps AI

AI-powered Franchise Operations Management System — React + Vite + Tailwind
frontend, FastAPI backend, PostgreSQL database. Built end-to-end: architecture,
schema, all 8 backend domains with a real AI layer, all 10 frontend pages
live-wired to the backend, security-reviewed RBAC, and realistic demo data.

## What's in this project

**Backend (`backend/`)** — FastAPI, 94 REST endpoints across:
Auth (JWT, RBAC with region-scoped regional managers) · Outlets · Sales ·
Inventory (incl. suppliers, batch/expiry tracking) · Staff (incl. payroll,
shifts, leave management) · Marketing (campaigns, ROI, customer segmentation) ·
Audit (compliance scoring, findings, evidence, 4-stage approval workflow) ·
AI Insights (forecasting, health scores, anomaly detection, executive
summaries) · Recommendations · Alerts/Notifications · Reports (PDF/Excel/CSV) ·
Data Validation (CSV/Excel upload + cleaning) · Admin (user/permission
management) · Search.

**AI layer** is real, explainable statistics — not a black box and not a
hosted LLM call: linear regression for forecasting, weighted composite
scoring for health scores, z-score/IQR for anomaly detection, a rule engine
for recommendations, template-based NLG for executive summaries. Every
number displayed traces back to an actual computation over the data in
Postgres, nothing hardcoded.

**Frontend (`frontend/`)** — React + Vite + Tailwind, 10 pages (Dashboard,
Outlet/Inventory/Staff/Marketing/Audit Agents, Intelligence Engine,
Recommendations, Reports, Admin, Settings), all fetching live data via
React Query — no dummy data. Dark mode, toast notifications, global search
with keyboard navigation, glassmorphism design system throughout.

**Database** — 28 PostgreSQL tables, fully normalized (regions and
permissions are real tables, not string columns), realistic demo data:
10 outlets, 42 products across 8 categories, 6 suppliers, inventory with
deliberate low-stock/out-of-stock/overstock/expiring/expired scenarios,
90 days of sales history, 10 marketing campaigns spanning high/average/low
performers, and a full audit workflow (10 audits, findings, evidence,
4-stage approvals) — all internally consistent, every foreign key verified
to point at a real row.

## Setup

```bash
# 1. Database
createdb franchiseops
cd backend
cp .env.example .env    # edit DATABASE_URL and SECRET_KEY
pip install -r requirements.txt

# 2. Seed (creates schema + loads all demo data, safe to re-run)
python seed.py
#   python seed.py --reset   # wipes and recreates everything first

# 3. Run
uvicorn app.main:app --reload
```
Swagger docs: http://localhost:8000/docs

```bash
# 4. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```
Opens at http://localhost:5173, proxying `/api` to the backend automatically.

Register your first account via the app's Register page, or `POST
/api/v1/auth/register` directly — pick `admin` role to see the whole network.

## Testing

```bash
cd backend && pytest
```
Includes ~90 test functions: unit tests for every AI service (forecasting,
anomaly detection, recommender, NLG, data validation — all pure functions,
no DB needed), integration tests for auth/RBAC/regional-scoping/leave/
permissions, and a static-analysis regression guard
(`test_query_scoping_guard.py`) that fails the build if any future endpoint
queries outlet-owned data without properly scoping it.

## Deployment

- **Backend → Render**: `backend/render.yaml` (web service + free Postgres),
  or `backend/Dockerfile` for any container host.
- **Frontend → Vercel**: `frontend/vercel.json`. Set `VITE_API_BASE_URL` to
  your deployed backend URL.
- Run `python seed.py` against the production database after deploying.

## Security notes

RBAC went through four rounds of review that found and fixed real
authorization gaps — not hypothetical ones:
- `regional_manager` originally had unrestricted network-wide access
  (identical to `admin`); fixed by adding a real `region` field and scoping
  every relevant query against it.
- Several endpoints (marketing campaigns, audit findings/risk, report
  generation, recommendation refresh, stock-transfer suggestions, data
  import) leaked or allowed writes to data outside the caller's authorized
  scope. All fixed.
- Password reset tokens are SHA-256 hashed before storage, never stored raw.
- Auth endpoints are rate-limited against brute force.
- The regression guard above exists specifically because manual review kept
  finding new instances of the same bug class — it's a structural fix, not
  another one-off patch.

## Honest limitations

- **Nothing in this project has been run in a live environment.** This was
  built in a sandbox with no network access, so `pip install`, `npm
  install`, a live PostgreSQL connection, an actual `pytest` run, and any
  real deployment were never possible. Every verification claim in this
  repo is either static analysis (code compiles, imports resolve, all 94
  backend routes match all 91 frontend calls, zero scoping-guard
  violations) or direct execution of the ~45 dependency-free pure functions
  (AI math, data validation, rate limiter). That is real signal, but it is
  not the same as "I watched this run." The first real `pip install` or
  `npm install` may surface a version mismatch or typo that static checks
  can't catch — if so, the fix is almost always small.
- Email sending is real (SMTP via `smtplib`) but unconfigured by default —
  no mail account exists in this sandbox to configure it with. Password
  reset falls back to returning the token in the API response until you set
  `SMTP_*` in `.env`.
- Alembic migrations aren't generated — `schema.sql` is the source of truth
  and `seed.py` applies it directly.
- The recommendation-refresh job is manual (`POST /recommendations/refresh`)
  rather than scheduled, since it clears open recommendations first and
  auto-running that could wipe someone's in-progress triage. The alert
  scanner does run automatically, every 15 minutes.

## Repository layout
See `docs/ARCHITECTURE.md` for the full folder structure, system diagram,
and naming conventions.
