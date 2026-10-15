from pydantic import BaseModel

from backend.app.schemas.cafe import CafeRead
from backend.app.schemas.category import CategoryRead
from backend.app.schemas.product import ProductRead


class MenuCategory(CategoryRead):
    products: list[ProductRead]


class CafeMenuRead(BaseModel):
    cafe: CafeRead
    categories: list[MenuCategory]
