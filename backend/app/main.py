from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.api.routes.legacy import router as legacy_router
from backend.app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# Versioned API for new clients.
app.include_router(api_router, prefix="/api/v1")
# Compatibility routes expected by the existing Cafe Aramesh frontend.
app.include_router(legacy_router, prefix="/api")


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {"name": settings.project_name, "docs": "/docs" if settings.debug else "disabled"}
