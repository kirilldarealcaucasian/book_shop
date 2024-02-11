from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime


class Id(BaseModel):
    id: int


class Config(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductBaseS(Config):
    name: str
    description: str
    price_per_unit: int
    number_in_stock: int


class CategoryBaseS(Config):
    name: str


class OrderBaseS(Config):
    user_id: int


class UserBaseS(Config):
    name: str
    email: EmailStr
    is_admin: bool


class ImageBaseS(Config):
    pass



