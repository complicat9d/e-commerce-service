from pydantic import BaseModel
from typing import Optional


class UserBaseSchema(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    lang: str


class UserSchema(UserBaseSchema):
    pass


class UserCreateSchema(UserBaseSchema):
    pass


class UserUpdateSchema(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    lang: Optional[str] = None
