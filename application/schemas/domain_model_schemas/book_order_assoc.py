from pydantic import BaseModel


class BookOrderAssocS(BaseModel):
    order_id: int | None
    book_id: str | None
    count_ordered: int | None