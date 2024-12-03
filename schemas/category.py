from pydantic import BaseModel


class CategoryBaseSchema(BaseModel):
    id: int
    name: str
    products_amount: int


class CategorySchema(CategoryBaseSchema):
    pass


class CategoryUpdateSchema(CategoryBaseSchema):
    pass
