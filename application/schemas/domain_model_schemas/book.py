from pydantic import BaseModel, UUID4, ConfigDict


class BookS(BaseModel, validate_assignment=True):
    id: UUID4 | None
    isbn: str | None
    name: str | None
    description: str | None
    price_per_unit: float | None
    price_with_discount: float | None
    number_in_stock: int | None
    category_id: int | None
    rating: float | None
    discount: int | None

    class Config:
        orm_mode = True
        model_config = ConfigDict(
            from_attributes=True,
        )