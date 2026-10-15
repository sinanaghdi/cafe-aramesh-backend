from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing import Annotated


FourDigitCode = Annotated[str, StringConstraints(pattern=r"^\d{4}$")]


class OrderItemIn(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=50)
    notes: str = Field(default="", max_length=300)


class OrderIn(BaseModel):
    table_number: int = Field(gt=0)
    items: list[OrderItemIn] = Field(min_length=1, max_length=50)
    notes: str = Field(default="", max_length=500)


class LoginIn(BaseModel):
    pin: str = Field(min_length=1, max_length=64)


class VerifyIn(BaseModel):
    code: FourDigitCode


class StatusIn(BaseModel):
    status: str


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_name: str
    quantity: int
    unit_price: int
    notes: str = ""


class OrderRead(BaseModel):
    id: int
    table_number: int
    status: str
    subtotal: int
    total: int
    notes: str
    created_at: str
    items: list[dict]
