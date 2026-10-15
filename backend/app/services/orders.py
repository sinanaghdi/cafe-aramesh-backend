import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from backend.app.core.order_config import CONFIRMATION_TTL_MINUTES
from backend.app.models.cafe import Cafe
from backend.app.models.category import Category
from backend.app.models.product import Product
from backend.app.models.order import CafeTable, ConfirmationCode, Order, OrderItem


def _now() -> datetime:
    return datetime.now(timezone.utc)


def serialize(order: Order) -> dict:
    return {
        "id": order.id,
        "table_number": order.table.table_number if order.table else 0,
        "status": order.status,
        "subtotal": order.subtotal,
        "total": order.total,
        "notes": order.notes,
        "created_at": order.created_at.isoformat() if order.created_at else _now().isoformat(),
        "items": [
            {
                "id": item.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "notes": item.notes,
            }
            for item in order.items
        ],
    }


def _order_query():
    return select(Order).options(
        joinedload(Order.table),
        selectinload(Order.items).joinedload(OrderItem.product),
    )


def create_order(db: Session, data):
    cafe = db.scalar(select(Cafe).where(Cafe.is_active.is_(True)).order_by(Cafe.id).limit(1))
    if cafe is None:
        raise HTTPException(status_code=503, detail="cafe_not_configured")

    table = db.scalar(select(CafeTable).where(
        CafeTable.cafe_id == cafe.id,
        CafeTable.table_number == data.table_number,
    ))
    if table is None:
        raise HTTPException(status_code=404, detail="table_not_found")

    order = Order(cafe_id=cafe.id, table_id=table.id, subtotal=0, total=0, notes=data.notes)
    total = 0
    for line in data.items:
        product = db.scalar(
            select(Product)
            .join(Category, Product.category_id == Category.id)
            .where(
                Product.id == line.product_id,
                Category.cafe_id == cafe.id,
                Category.is_active.is_(True),
                Product.is_available.is_(True),
            )
        )
        if product is None:
            raise HTTPException(status_code=404, detail="product_not_found")
        total += int(product.price) * line.quantity
        order.items.append(OrderItem(
            product_id=product.id,
            quantity=line.quantity,
            unit_price=int(product.price),
            notes=line.notes,
        ))

    order.subtotal = order.total = total
    db.add(order)
    db.flush()

    # Avoid accidentally issuing the same live code for two pending orders.
    live_codes = set(db.scalars(select(ConfirmationCode.code).where(
        ConfirmationCode.used_at.is_(None),
        ConfirmationCode.expires_at > _now(),
    )).all())
    for _ in range(100):
        code = f"{secrets.randbelow(10000):04d}"
        if code not in live_codes:
            break
    else:
        db.rollback()
        raise HTTPException(status_code=503, detail="confirmation_code_unavailable")

    db.add(ConfirmationCode(
        order_id=order.id,
        code=code,
        expires_at=_now() + timedelta(minutes=CONFIRMATION_TTL_MINUTES),
    ))
    db.commit()
    db.refresh(order)
    return db.scalar(_order_query().where(Order.id == order.id)), code


def verify(db: Session, code: str):
    confirmation = db.scalar(
        select(ConfirmationCode)
        .where(ConfirmationCode.code == code, ConfirmationCode.used_at.is_(None))
        .order_by(ConfirmationCode.created_at.desc(), ConfirmationCode.id.desc())
    )
    if confirmation is None:
        raise HTTPException(status_code=404, detail="invalid_code")
    if confirmation.expires_at <= _now():
        raise HTTPException(status_code=410, detail="expired")
    order = db.scalar(_order_query().where(Order.id == confirmation.order_id))
    if order is None:
        raise HTTPException(status_code=404, detail="order_not_found")
    if order.status != "PENDING_WAITER":
        raise HTTPException(status_code=409, detail="already_processed")
    return confirmation, order


def approve(db: Session, order_id: int):
    order = db.scalar(_order_query().where(Order.id == order_id))
    if order is None:
        raise HTTPException(status_code=404, detail="order_not_found")
    if order.status != "PENDING_WAITER":
        raise HTTPException(status_code=409, detail="invalid_transition")
    confirmation = db.scalar(
        select(ConfirmationCode)
        .where(ConfirmationCode.order_id == order_id, ConfirmationCode.used_at.is_(None))
        .order_by(ConfirmationCode.created_at.desc())
    )
    if confirmation is None or confirmation.expires_at <= _now():
        raise HTTPException(status_code=410, detail="expired")
    confirmation.used_at = _now()
    order.status = "CONFIRMED"
    order.confirmed_at = _now()
    db.commit()
    return db.scalar(_order_query().where(Order.id == order_id))


def reject(db: Session, order_id: int, reason: str):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order_not_found")
    if order.status != "PENDING_WAITER":
        raise HTTPException(status_code=409, detail="invalid_transition")
    order.status = "REJECTED"
    if reason:
        order.notes = (f"{order.notes} | {reason}").strip(" |")[:500]
    db.commit()
    return {"id": order.id, "status": order.status}


def update_status(db: Session, order_id: int, new_status: str):
    transitions = {"CONFIRMED": "PREPARING", "PREPARING": "READY", "READY": "SERVED"}
    order = db.scalar(_order_query().where(Order.id == order_id))
    if order is None:
        raise HTTPException(status_code=404, detail="order_not_found")
    if transitions.get(order.status) != new_status:
        raise HTTPException(status_code=409, detail="invalid_transition")
    order.status = new_status
    if new_status == "SERVED":
        order.served_at = _now()
    db.commit()
    return db.scalar(_order_query().where(Order.id == order_id))
