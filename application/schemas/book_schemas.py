from uuid import UUID

from application.schemas.base_schemas import BookBaseS
from pydantic import BaseModel, Field


class ReturnBookS(BookBaseS):
    id: UUID
    isbn: str
    genre_names: list[str]
    rating: float | None
    discount: int


class CreateBookS(BookBaseS):
    isbn: str = Field(min_length=1)
    genre_name: str = Field(min_length=1)
    rating: float | None = Field(ge=0)
    discount: int | None = Field(ge=0)


class UpdateBookS(BookBaseS):
    isbn: str = Field(min_length=1)
    description: str
    genre_name: str = Field(min_length=1)
    rating: float = Field(ge=0)
    discount: int = Field(ge=0)


class UpdatePartiallyBookS(BaseModel):
    name: str | None = Field(min_length=1)
    description: str | None = None
    price_per_unit: float | None = Field(ge=0)
    number_in_stock: int | None = Field(ge=1)
    genre_name: str | None = Field(min_length=1)
    rating: float | None = None
    discount: int | None = None


class BookSummaryS(BaseModel):
    name: str
    count_ordered: int
    total_price: float




