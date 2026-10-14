from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.cafe import CafeRead
from backend.app.schemas.menu import CafeMenuRead
from backend.app.services.menu import cafe_details, cafe_menu

router = APIRouter()


@router.get("/{cafe_id}", response_model=CafeRead, summary="Get public cafe details")
def read_cafe(cafe_id: int, db: Session = Depends(get_db)) -> CafeRead:
    cafe = cafe_details(db, cafe_id)
    if cafe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cafe not found")
    return cafe


@router.get("/{cafe_id}/menu", response_model=CafeMenuRead, summary="Get an active cafe menu")
def read_cafe_menu(cafe_id: int, db: Session = Depends(get_db)) -> CafeMenuRead:
    cafe = cafe_menu(db, cafe_id)
    if cafe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cafe not found")
    return CafeMenuRead.model_validate({
        "cafe": cafe,
        "categories": [
            {**category.__dict__, "products": category.products}
            for category in cafe.categories
        ],
    })
