"""Import model classes here so Alembic can discover their metadata."""

from backend.app.db.base import Base
from backend.app.models.cafe import Cafe
from backend.app.models.category import Category
from backend.app.models.order import CafeTable, ConfirmationCode, Order, OrderItem
from backend.app.models.product import Product

__all__ = [
    "Base", "Cafe", "Category", "Product",
    "CafeTable", "Order", "OrderItem", "ConfirmationCode",
]
