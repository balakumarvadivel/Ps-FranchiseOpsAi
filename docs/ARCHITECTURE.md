# FranchiseOps AI — System Architecture (Phase 1)

## 1. Complete Folder Structure

```
franchiseops-ai/
├── frontend/                          # React + Vite + Tailwind
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── common/                # Button, Card, Modal, Table, Badge, ProgressBar
│   │   │   ├── layout/                # Sidebar, Navbar, Footer, PageContainer
│   │   │   ├── charts/                # LineChart, AreaChart, BarChart, PieChart, RadarChart, Heatmap, Gauge
│   │   │   └── ai/                    # AIInsightCard, AIRecommendationCard, AISummaryBanner
│   │   ├── pages/
│   │   │   ├── auth/                  # Login, Register, ForgotPassword
│   │   │   ├── dashboard/             # ExecutiveDashboard
│   │   │   ├── outlet-agent/
│   │   │   ├── inventory-agent/
│   │   │   ├── staff-agent/
│   │   │   ├── marketing-agent/
│   │   │   ├── audit-agent/
│   │   │   ├── intelligence-engine/
│   │   │   ├── recommendations/
│   │   │   ├── reports/
│   │   │   └── settings/
│   │   ├── features/                  # Redux/Zustand slices or React Query hooks, grouped by domain
│   │   │   ├── auth/
│   │   │   ├── outlets/
│   │   │   ├── inventory/
│   │   │   ├── staff/
│   │   │   ├── marketing/
│   │   │   ├── audit/
│   │   │   └── ai/
│   │   ├── services/                  # api.js (axios instance), *Service.js per domain
│   │   ├── hooks/                     # useAuth, useTheme, useDebounce, usePagination
│   │   ├── context/                   # AuthContext, ThemeContext
│   │   ├── routes/                    # AppRoutes.jsx, ProtectedRoute.jsx, roleGuards.js
│   │   ├── utils/                     # formatters, validators, constants
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
│
├── backend/                           # FastAPI
│   ├── app/
│   │   ├── main.py                    # App entrypoint, router registration, middleware
│   │   ├── config.py                  # Settings (env vars)
│   │   ├── database.py                # SQLAlchemy engine/session
│   │   ├── models/                    # SQLAlchemy ORM models, 1 file per domain
│   │   ├── schemas/                   # Pydantic request/response models
│   │   ├── routers/                   # APIRouter per domain (auth, outlets, sales, ...)
│   │   ├── core/                      # security.py (JWT/hash), deps.py (get_db, get_current_user, RBAC)
│   │   ├── services/                  # Business logic + AI services (kept out of routers)
│   │   │   └── ai/                    # forecasting.py, health_score.py, anomaly.py, recommender.py, nlg_summary.py
│   │   ├── middleware/                # logging.py, error_handler.py, rate_limit.py
│   │   └── utils/                     # pagination, file export (pdf/excel/csv)
│   ├── alembic/                       # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── database/
│   ├── schema.sql                     # Full DDL
│   ├── seed.sql                       # Sample/dummy data
│   └── ERD.png / ERD.md
│
├── docs/
│   ├── ARCHITECTURE.md                # This file
│   └── API.md                         # Auto-generated via FastAPI /docs (Swagger) + notes
│
└── README.md
```

---

## 2. System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                             │
│   React + Vite SPA  →  Tailwind UI  →  Recharts  →  Framer Motion    │
└───────────────────────────────┬────────────────────────────────────--┘
                                 │ HTTPS / REST (JSON) + JWT Bearer
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       FASTAPI APPLICATION LAYER                      │
│  Middleware: CORS → Logging → Auth (JWT) → RBAC → Error Handler      │
│  Routers: auth · outlets · sales · inventory · staff · marketing ·   │
│           audit · ai_insights · recommendations · reports · alerts   │
└───────┬───────────────────────────────┬───────────────────────────--─┘
        │                               │
        ▼                               ▼
┌──────────────────────┐      ┌────────────────────────────────────┐
│   SERVICE LAYER       │      │        AI SERVICE LAYER            │
│  Business rules,       │      │  forecasting.py (moving avg /      │
│  validation, CRUD       │      │   regression), health_score.py,   │
│  orchestration          │      │   anomaly.py, recommender.py,     │
│                         │      │   nlg_summary.py                  │
└───────────┬────────────┘      └───────────────┬────────────────────┘
            │                                    │
            ▼                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    SQLAlchemy ORM (models + sessions)                 │
└───────────────────────────────┬────────────────────────────────────--┘
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          PostgreSQL Database                         │
│   users · roles · outlets · sales · inventory · employees · ...      │
└──────────────────────────────────────────────────────────────────────┘

Deployment:  Frontend → Vercel (static SPA)   Backend + DB → Render
```

---

## 3. Frontend Architecture

- **Pattern**: Feature-based (not type-based) — each domain (`outlets`, `inventory`, `staff`...) owns its own API hooks, and shares `components/common` and `components/charts`.
- **State**: Server state via React Query (caching, refetch, background sync); lightweight client/UI state (theme, sidebar collapse, filters) via React Context or Zustand — no need for Redux at this scale.
- **Data flow**: Page → feature hook (`useOutlets()`) → `services/outletService.js` (axios) → FastAPI → response cached by React Query → rendered by chart/table components.
- **Routing**: `react-router-dom` v6, nested routes under a `DashboardLayout` (sidebar + navbar persist across pages); `ProtectedRoute` wraps everything except `/login`, `/register`, `/forgot-password`.
- **Theming**: Tailwind `dark:` variant driven by a `ThemeContext` that toggles a class on `<html>`, persisted in `localStorage`.

## 4. Backend Architecture

- **Pattern**: Layered — `router → service → model`. Routers only handle HTTP concerns (validation via Pydantic, status codes); all business logic lives in `services/`, keeping routers thin and testable.
- **Auth**: JWT access tokens (`python-jose`), password hashing via `passlib[bcrypt]`. `core/deps.py` exposes `get_current_user` and role-based dependencies (`require_role("admin")`) used to protect routes.
- **AI layer**: Isolated under `services/ai/` so it can be swapped for real ML models later without touching routers. Each AI service is a pure function: takes data in, returns a typed result (score, forecast, recommendation list) — no direct DB or HTTP coupling, which makes it unit-testable.
- **Error handling**: Centralized exception handlers in `middleware/error_handler.py` translate domain exceptions (e.g. `NotFoundError`, `ValidationError`) into consistent JSON error responses.
- **Docs**: FastAPI auto-generates OpenAPI/Swagger at `/docs` and ReDoc at `/redoc` — this is the living API architecture document.

## 5. Database Architecture

- **Engine**: PostgreSQL, accessed via SQLAlchemy 2.0 ORM + Alembic for migrations (no manual schema drift).
- **Design principles**: every table has a surrogate `SERIAL` PK; foreign keys enforce referential integrity (e.g. `sales.outlet_id → outlets.id`); composite indexes on hot query paths (`outlet_id + date` for sales/attendance); `ON DELETE CASCADE` only where child rows are meaningless without the parent (batches, shifts), `RESTRICT`-by-default elsewhere.
- **Scalability**: date-range queries (sales, attendance) are indexed for time-series access; consider partitioning `sales` by month once row counts grow (documented, not needed at student-project scale).

## 6. API Architecture

- **Style**: REST, resource-oriented, versioned under `/api/v1/`.
- **Conventions**: `GET /outlets`, `GET /outlets/{id}`, `POST /outlets`, `PUT /outlets/{id}`, `DELETE /outlets/{id}`; nested resources where ownership is exclusive (`GET /outlets/{id}/inventory`).
- **AI endpoints** are read-only computed views, e.g. `GET /outlets/{id}/health-score`, `GET /ai/forecast?outlet_id=&range=30d`, `GET /ai/recommendations`.
- **Pagination**: `?page=&page_size=` with `X-Total-Count` header; **filtering**: `?region=&status=&date_from=&date_to=`.
- **Auth**: `Authorization: Bearer <token>` on every protected route; `POST /auth/login`, `/auth/register`, `/auth/forgot-password` are public.

## 7. AI Architecture

Given this is a student/demo system, "AI" is implemented as transparent, explainable statistical/rule-based logic rather than opaque deep learning — appropriate for a viva/defense where you need to explain exactly how a score was computed:

| Module | Technique |
|---|---|
| Revenue/Sales Forecasting | Moving average + linear regression trend line, confidence band from residual variance |
| Outlet/Inventory/Staff Health Score | Weighted composite of normalized sub-metrics (documented weights, not a black box) |
| Anomaly/Fraud/Risk Detection | Z-score / IQR-based outlier detection on sales, expenses, audit scores |
| Root Cause Analysis | Rule engine: correlates health sub-metric drops with the largest negative deltas |
| Recommendations | Rule engine + priority scoring (impact × confidence) |
| Natural Language Summary | Template-based NLG — structured data filled into professionally-worded sentence templates |

This can later be upgraded to real ML (e.g. Prophet/ARIMA for forecasting, XGBoost for attrition) without changing the API contract, since each service returns the same typed response shape.

## 8. Routing Structure (Frontend)

```
/login  /register  /forgot-password
/app                                → DashboardLayout (protected)
  /app/dashboard                    → Executive Dashboard
  /app/outlets                      → Outlet Performance Agent
  /app/inventory                    → Inventory Agent
  /app/staff                        → Staff Agent
  /app/marketing                    → Marketing Agent
  /app/audit                        → Audit Agent
  /app/intelligence                 → Franchise Intelligence Engine
  /app/recommendations              → Business Recommendation Engine
  /app/reports                      → Reports
  /app/settings                     → Settings
```
Role guards: `outlet_manager` is redirected/scoped to their own `outlet_id` on every page; `admin` and `regional_manager` see the full network (regional_manager filtered to their region).

## 9. Component Hierarchy (per agent page — repeatable pattern)

```
<AgentPage>
 ├─ <PageHeader title subtitle actions=[AIAnalysis, Compare, Export, Refresh] />
 ├─ <KPIGrid> → <KPICard /> × N (value, trend, sparkline, AI badge)
 ├─ <FiltersBar> → <SearchInput/> <RegionFilter/> <OutletFilter/> <DateRangePicker/>
 ├─ <ChartSection> → <ChartCard title> → <LineChart|AreaChart|BarChart|RadarChart/>
 ├─ <AIInsightPanel> → <AIInsightCard/> × N
 ├─ <DataTable> → sortable columns, <StatusBadge/>, pagination
 └─ <AIRecommendationPanel> → <RecommendationCard priority reason impact confidence/>
```
Every piece above is a shared component from `components/common` and `components/charts`, parameterized by props/data — agent pages compose them rather than redefining UI.

## 10. Naming Conventions

- **React components**: `PascalCase` files and exports (`OutletHealthGauge.jsx`).
- **Hooks**: `useCamelCase` (`useOutletPerformance.js`).
- **API service functions**: verb-first camelCase (`getOutlets`, `createRecommendation`).
- **Python**: `snake_case` for functions/variables, `PascalCase` for classes (`OutletService`, `SaleCreate`).
- **DB tables/columns**: `snake_case`, plural table names (`outlets`, `audit_reports`), FK columns as `{table_singular}_id` (`outlet_id`).
- **API routes**: kebab-case for multi-word segments (`/ai/forecast-revenue`), plural nouns for collections.
- **Env vars**: `UPPER_SNAKE_CASE`.

## 11. Development Roadmap

| Phase | Deliverable |
|---|---|
| 1 | Architecture (this document) |
| 2 | PostgreSQL schema, ERD, seed data |
| 3 | FastAPI backend — auth, core CRUD APIs, error handling |
| 4 | React frontend shell — layout, routing, dummy-data dashboard |
| 5 | Data validation & upload module |
| 6 | Outlet Performance Agent (full) |
| 7 | Inventory Agent (full) |
| 8 | Staff Agent |
| 9 | Marketing Agent |
| 10 | Audit Agent |
| 11 | Franchise Intelligence Engine |
| 12 | Business Recommendation Engine |
| 13 | Executive Dashboard (final polish) |
| 14 | Integration — wire frontend to live backend, replace dummy data, deploy |

## 12. Module Communication

- **Frontend ↔ Backend**: exclusively over REST/JSON with JWT bearer auth; no direct DB access from the client.
- **Router → Service → Model**: routers never touch SQLAlchemy models directly — they call a service function, which is the only thing that queries/mutates the DB. This means business logic (e.g. "what counts as low stock") lives in exactly one place.
- **Domain services → AI services**: e.g. `OutletService.get_dashboard()` calls `ai.health_score.compute(outlet_data)` and merges the result into its response — AI services are pure functions with no knowledge of HTTP or the DB session.
- **Cross-agent data**: the **Franchise Intelligence Engine** is the only service allowed to read from multiple domains (sales, inventory, staff, marketing, audit) at once, to compute the composite Business Health Score — this avoids every agent needing to know about every other agent.
- **Recommendations**: generated by the Recommendation Engine, which subscribes to outputs of all agents + the Intelligence Engine, then writes rows into the shared `recommendations` table, which the frontend polls/queries — agents themselves never write recommendations directly.
