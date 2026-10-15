from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.product import ProductRead
from backend.app.services.menu import available_products

router = APIRouter()


@router.get("/", response_model=list[ProductRead], summary="List available products")
def read_products(
    category_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    return available_products(db, category_id)
