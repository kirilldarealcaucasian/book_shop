from uuid import UUID

from pydantic import BaseModel

from application.schemas import ReturnBookS
from application.schemas.order_schemas import AssocBookS


class ReturnCartS(BaseModel):
    cart_id: UUID
    books: list[AssocBookS]



class CreateCartS(BaseModel):
    session_id: UUID


class AddBookToCartS(BaseModel):
    book_id: UUID | str | int
    session_id: UUID | str | int
    quantity: int

