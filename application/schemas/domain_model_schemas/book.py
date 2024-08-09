from pydantic import BaseModel


class BookS(BaseModel):
    id: str | None
    isbn: str | None
    name: str | None
    description: str | None
    price_per_unit: float | None
    price_with_discount: float | None
    number_in_stock: int | None
    category_id: int | None
    rating: float | None
    discount: int | None