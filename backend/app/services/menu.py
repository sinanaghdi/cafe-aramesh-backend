from sqlalchemy.orm import Session

from backend.app.repositories.menu import (
    get_active_cafe,
    get_active_cafe_menu,
    list_active_categories,
    list_available_products,
)


def cafe_details(db: Session, cafe_id: int):
    return get_active_cafe(db, cafe_id)


def cafe_menu(db: Session, cafe_id: int):
    return get_active_cafe_menu(db, cafe_id)


def cafe_categories(db: Session, cafe_id: int):
    return list_active_categories(db, cafe_id)


def available_products(db: Session, category_id: int | None = None):
    return list_available_products(db, category_id)
