from pydantic import BaseModel


class CartItemS(BaseModel):
    session_id: str | None
    book_id: str | None
    quantity: int | None