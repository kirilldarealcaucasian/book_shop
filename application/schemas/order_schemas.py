from pydantic import BaseModel, EmailStr, Field
from application.schemas.book_schemas import BookSummaryS
from application.schemas.base_schemas import OrderBaseS
from datetime import datetime


class CreateOrderS(OrderBaseS):
    order_status: str | None = None


class UpdateOrderS(OrderBaseS):
    pass


class UpdatePartiallyOrderS(BaseModel):
    order_status: str | None
    order_date: datetime | None = None
    total_sum: float | None = None


class OrderSummaryS(BaseModel):
    username: str
    email: str
    books: list[BookSummaryS]


class AssocBookS(BaseModel):
    book_title: str
    authors: list[str]
    genre_name: str
    rating: int
    discount: int
    count_ordered: int
    price_per_unit: float


class ReturnOrderS(BaseModel):
    order_id: int
    books: list[AssocBookS]


class ShortenedReturnOrderS(BaseModel):
    owner_name: str
    owner_email: EmailStr
    order_id: int
    order_status: str
    total_sum: float | None = None
    order_date: datetime | None = None


class ReturnOrderIdS(ReturnOrderS):
    order_id: int


class QuantityS(BaseModel):
    quantity: int = Field(ge=0)
