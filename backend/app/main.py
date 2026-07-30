from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.error_handler import register_exception_handlers

# Ensure all models are registered on Base.metadata before anything queries the DB.
import app.models  # noqa: F401

from app.routers import auth, outlets, sales, inventory, ai_insights

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
)
app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

# --- Routers ------------------------------------------------------------
app.include_router(auth.router)
app.include_router(outlets.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(ai_insights.router)

# TODO (next phases): staff.router, marketing.router, audit.router,
# recommendations.router, reports.router, notifications.router — same
# router → service → model pattern as outlets/sales/inventory above.


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
