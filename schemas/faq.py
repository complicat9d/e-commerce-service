from pydantic import BaseModel


class FAQBaseSchema(BaseModel):
    title: str
    text: str


class FAQSchema(FAQBaseSchema):
    id: int


class FAQCreateSchema(FAQBaseSchema):
    pass
