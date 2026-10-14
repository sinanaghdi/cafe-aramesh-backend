from fastapi import APIRouter

from backend.app.api.routes.cafes import router as cafes_router
from backend.app.api.routes.categories import router as categories_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.products import router as products_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(cafes_router, prefix="/cafes", tags=["Cafes"])
api_router.include_router(categories_router, prefix="/categories", tags=["Categories"])
api_router.include_router(products_router, prefix="/products", tags=["Products"])
