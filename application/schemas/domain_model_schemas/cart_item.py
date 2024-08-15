from pydantic import BaseModel
from uuid import UUID

class CartItemS(BaseModel):
    session_id: UUID | None
    book_id: str | None
    quantity: int | None