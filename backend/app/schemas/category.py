from pydantic import BaseModel, ConfigDict


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cafe_id: int
    name: str
    slug: str
    description: str | None
    sort_order: int
    is_active: bool
