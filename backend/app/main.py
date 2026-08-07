from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.error_handler import register_exception_handlers

# Ensure all models are registered on Base.metadata before anything queries the DB.
import app.models  # noqa: F401

from app.routers import (
    auth, outlets, sales, inventory, ai_insights,
    staff, marketing, audit, alerts, recommendations, reports, data_validation,
    users, search, permissions,
)
from app.services.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Franchise Operations Management System — REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middleware -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)
app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

# --- Routers ------------------------------------------------------------
app.include_router(auth.router)
app.include_router(outlets.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(ai_insights.router)
app.include_router(staff.router)
app.include_router(marketing.router)
app.include_router(audit.router)
app.include_router(alerts.router)
app.include_router(recommendations.router)
app.include_router(reports.router)
app.include_router(data_validation.router)
app.include_router(users.router)
app.include_router(search.router)
app.include_router(permissions.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
def on_startup():
    if settings.ENV != "test":
        start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()
