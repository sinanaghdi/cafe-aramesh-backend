from pydantic import BaseModel, ConfigDict


class CafeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    address: str | None
    phone: str | None
    is_active: bool
