from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.category import CategoryRead
from backend.app.services.menu import cafe_categories, cafe_details

router = APIRouter()


@router.get("/", response_model=list[CategoryRead], summary="List active categories for a cafe")
def read_categories(
    cafe_id: int = Query(gt=0),
    db: Session = Depends(get_db),
) -> list[CategoryRead]:
    if cafe_details(db, cafe_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cafe not found")
    return cafe_categories(db, cafe_id)
