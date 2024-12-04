from pydantic import BaseModel
from typing import Optional


class CartBaseSchema(BaseModel):
    user_id: int
    product_id: int
    amount: int


class CartSchema(CartBaseSchema):
    cost: float
    address: Optional[str] = None


class CartCreateSchema(CartBaseSchema):
    pass
