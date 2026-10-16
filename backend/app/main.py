from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .routers import checkins, dashboard, members, plans, trainers

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Gym management API: members, membership plans, trainers and attendance.",
)
app.add_middleware(
    CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"]
)
Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)

for router in (plans.router, trainers.router, members.router, checkins.router, dashboard.router):
    app.include_router(router)


@app.get("/", tags=["system"])
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["system"])
def health():
    """Liveness: the process is up. Deliberately does not touch the database."""
    return {"status": "UP"}


@app.get("/ready", tags=["system"])
def ready(db: Session = Depends(get_db)):
    """Readiness: the database is reachable and migrations have created the schema."""
    try:
        db.execute(text("SELECT 1 FROM members LIMIT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database not ready") from exc
    return {"status": "READY"}
