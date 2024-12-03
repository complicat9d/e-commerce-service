from pydantic import BaseModel
from typing import Optional


class ProductBaseSchema(BaseModel):
    category_id: int
    name: str
    photo: Optional[str] = None
    description: str
    cost: float


class ProductCreateSchema(ProductBaseSchema):
    pass


class ProductSchema(ProductBaseSchema):
    id: int
    amount: int
