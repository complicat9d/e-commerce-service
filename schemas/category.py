from pydantic import BaseModel


class CategoryBaseSchema(BaseModel):
    id: int
    name: str


class CategorySchema(CategoryBaseSchema):
    pass
