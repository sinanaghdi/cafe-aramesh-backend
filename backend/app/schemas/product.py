from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    slug: str
    description: str | None
    price: Decimal = Field(ge=0)
    image_url: str | None
    is_available: bool
    sort_order: int
