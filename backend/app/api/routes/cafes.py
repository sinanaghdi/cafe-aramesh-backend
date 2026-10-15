from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.cafe import CafeRead
from backend.app.schemas.menu import CafeMenuRead, MenuCategory
from backend.app.schemas.product import ProductRead
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

    categories = []
    for category in sorted(
        (item for item in cafe.categories if item.is_active),
        key=lambda item: (item.sort_order, item.id),
    ):
        products = [
            ProductRead.model_validate(product)
            for product in sorted(
                (item for item in category.products if item.is_available),
                key=lambda item: (item.sort_order, item.id),
            )
        ]
        categories.append(
            MenuCategory(
                id=category.id,
                cafe_id=category.cafe_id,
                name=category.name,
                slug=category.slug,
                description=category.description,
                sort_order=category.sort_order,
                is_active=category.is_active,
                products=products,
            )
        )

    return CafeMenuRead(cafe=CafeRead.model_validate(cafe), categories=categories)
