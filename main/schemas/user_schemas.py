from pydantic import Field, EmailStr, ConfigDict

from .base_schemas import UserBaseS, BaseModel, Id
from .product_order_schemas import ReturnOrderIdProductS


class RegisterUserS(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class LoginUserS(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UpdateUserS(UserBaseS):
    pass


class UpdatePartiallyUserS(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    is_admin: bool | None = False


class ReturnUserS(UserBaseS, Id):
    pass



class ReturnUserWithOrderS(BaseModel):
    user_name: str
    email: EmailStr
    orders: list[ReturnOrderIdProductS]

    # class Config:
    #     exclude = {"number_in_stock"}


class AuthenticatedUserS(UserBaseS, Id):
    pass



