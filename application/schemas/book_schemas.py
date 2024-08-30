from uuid import UUID

from application.schemas.base_schemas import BookBaseS
from pydantic import BaseModel, Field


class BookIdS(BaseModel):
    id: str | UUID


class ReturnBookS(BookIdS, BookBaseS):
    isbn: str
    genre_names: list[str]
    authors: list[str]
    rating: float | None
    discount: int


class CreateBookS(BookBaseS):
    isbn: str = Field(min_length=1)
    rating: float | None = Field(default=0, ge=0)
    discount: int | None = Field(default=0, ge=0)


class UpdateBookS(BookBaseS):
    isbn: str = Field(min_length=1)
    rating: float = Field(ge=0)
    discount: int = Field(ge=0)


class UpdatePartiallyBookS(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    isbn: str | None = None
    description: str | None = None
    price_per_unit: float | None = Field(default=None, ge=0)
    number_in_stock: int | None = Field(default=None, ge=0)
    rating: float | None = Field(default=None, ge=0)
    discount: int | None = Field(default=None, ge=0)


class BookSummaryS(BaseModel):
    name: str
    count_ordered: int
    total_price: float






