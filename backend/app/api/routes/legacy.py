from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from backend.app.core.order_config import WAITER_PIN
from backend.app.db.session import get_db
from backend.app.models.cafe import Cafe
from backend.app.models.category import Category
from backend.app.models.product import Product
from backend.app.models.order import CafeTable, Order, OrderItem
from backend.app.schemas.orders import LoginIn, OrderIn, StatusIn, VerifyIn
from backend.app.services.orders import approve, create_order, reject, serialize, update_status, verify

router = APIRouter()


def _legacy_product(product: Product) -> dict:
    return {
        "id": product.id,
        "cafe_id": product.category.cafe_id,
        "category_id": product.category_id,
        "name": product.name,
        "description": product.description or "",
        "price": int(product.price),
        "active": product.is_available,
        "badge": getattr(product, "badge", None),
        "image_url": product.image_url,
        "tags": getattr(product, "tags", ""),
    }


@router.get("/cafes/{cafe_id}")
def cafe(cafe_id: int, db: Session = Depends(get_db)):
    item = db.scalar(select(Cafe).where(Cafe.id == cafe_id, Cafe.is_active.is_(True)))
    if item is None:
        raise HTTPException(status_code=404, detail="not_found")
    return {"id": item.id, "name": item.name}


@router.get("/cafes/{cafe_id}/menu")
def menu(cafe_id: int, db: Session = Depends(get_db)):
    cafe_item = db.scalar(select(Cafe).where(Cafe.id == cafe_id, Cafe.is_active.is_(True)))
    if cafe_item is None:
        raise HTTPException(status_code=404, detail="not_found")
    products = db.scalars(
        select(Product).join(Category).options(joinedload(Product.category))
        .where(Category.cafe_id == cafe_id, Category.is_active.is_(True), Product.is_available.is_(True))
        .order_by(Category.sort_order, Product.sort_order, Product.id)
    ).all()
    return [_legacy_product(item) for item in products]


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    items = db.scalars(select(Category).where(Category.is_active.is_(True)).order_by(Category.sort_order, Category.id)).all()
    return [{
        "id": item.id, "cafe_id": item.cafe_id, "name": item.name,
        "sort_order": item.sort_order, "active": item.is_active,
    } for item in items]


@router.get("/products")
def products(db: Session = Depends(get_db)):
    items = db.scalars(
        select(Product).join(Category).options(joinedload(Product.category))
        .where(Category.is_active.is_(True), Product.is_available.is_(True))
        .order_by(Product.sort_order, Product.id)
    ).all()
    return [_legacy_product(item) for item in items]


@router.get("/products/{product_id}")
def product(product_id: int, db: Session = Depends(get_db)):
    item = db.scalar(select(Product).join(Category).options(joinedload(Product.category)).where(
        Product.id == product_id, Product.is_available.is_(True), Category.is_active.is_(True)
    ))
    if item is None:
        raise HTTPException(status_code=404, detail="not_found")
    return _legacy_product(item)


@router.post("/orders")
def post_order(data: OrderIn, db: Session = Depends(get_db)):
    order, code = create_order(db, data)
    return {**serialize(order), "confirmation_code": code}


@router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.scalar(select(Order).options(
        joinedload(Order.table), selectinload(Order.items).joinedload(OrderItem.product)
    ).where(Order.id == order_id))
    if order is None:
        raise HTTPException(status_code=404, detail="not_found")
    return serialize(order)


@router.get("/orders/{order_id}/status")
def order_status(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="not_found")
    return {"id": order.id, "status": order.status}


@router.post("/waiter/login")
def waiter_login(data: LoginIn):
    if not WAITER_PIN or data.pin != WAITER_PIN:
        raise HTTPException(status_code=401, detail="invalid_pin")
    return {"token": "demo-waiter-session"}


@router.get("/waiter/orders")
def waiter_orders(db: Session = Depends(get_db)):
    items = db.scalars(select(Order).options(
        joinedload(Order.table), selectinload(Order.items).joinedload(OrderItem.product)
    ).order_by(Order.created_at.desc(), Order.id.desc())).all()
    return [serialize(item) for item in items]


@router.post("/waiter/verify-code")
def verify_code(data: VerifyIn, db: Session = Depends(get_db)):
    _, order = verify(db, data.code)
    return serialize(order)


@router.post("/waiter/orders/{order_id}/approve")
def approve_order(order_id: int, db: Session = Depends(get_db)):
    return serialize(approve(db, order_id))


@router.post("/waiter/orders/{order_id}/reject")
def reject_order(order_id: int, body: dict, db: Session = Depends(get_db)):
    return reject(db, order_id, str(body.get("reason", ""))[:300])


@router.post("/waiter/orders/{order_id}/status")
def change_order_status(order_id: int, data: StatusIn, db: Session = Depends(get_db)):
    return serialize(update_status(db, order_id, data.status))
