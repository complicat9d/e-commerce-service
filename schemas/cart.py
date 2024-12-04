from pydantic import BaseModel
from typing import Optional


class CartBaseSchema(BaseModel):
    user_id: int
    product_id: int
    product_name: str
    amount: int


class CartSchema(CartBaseSchema):
    id: int
    cost: float
    address: Optional[str] = None
    is_being_delivered: bool


class CartCreateSchema(CartBaseSchema):
    cost: float
    product_amount: int


class CartUpdateSchema(BaseModel):
    user_id: int
    product_id: int
    address: Optional[str] = None
    is_being_delivered: Optional[bool] = None
