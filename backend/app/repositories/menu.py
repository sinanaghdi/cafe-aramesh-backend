from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.cafe import Cafe
from backend.app.models.category import Category
from backend.app.models.product import Product


def get_active_cafe(db: Session, cafe_id: int) -> Cafe | None:
    statement = select(Cafe).where(Cafe.id == cafe_id, Cafe.is_active.is_(True))
    return db.scalar(statement)


def get_active_cafe_menu(db: Session, cafe_id: int) -> Cafe | None:
    statement = (
        select(Cafe)
        .where(Cafe.id == cafe_id, Cafe.is_active.is_(True))
        .options(
            selectinload(Cafe.categories).selectinload(Category.products)
        )
    )
    cafe = db.scalar(statement)
    if cafe is None:
        return None

    cafe.categories[:] = sorted(
        (category for category in cafe.categories if category.is_active),
        key=lambda category: (category.sort_order, category.id),
    )
    for category in cafe.categories:
        category.products[:] = sorted(
            (product for product in category.products if product.is_available),
            key=lambda product: (product.sort_order, product.id),
        )
    return cafe


def list_active_categories(db: Session, cafe_id: int) -> list[Category]:
    statement = (
        select(Category)
        .where(Category.cafe_id == cafe_id, Category.is_active.is_(True))
        .order_by(Category.sort_order, Category.id)
    )
    return list(db.scalars(statement).all())


def list_available_products(db: Session, category_id: int | None = None) -> list[Product]:
    statement = (
        select(Product)
        .join(Category, Product.category_id == Category.id)
        .where(Product.is_available.is_(True), Category.is_active.is_(True))
        .order_by(Product.sort_order, Product.id)
    )
    if category_id is not None:
        statement = statement.where(Product.category_id == category_id)
    return list(db.scalars(statement).all())
