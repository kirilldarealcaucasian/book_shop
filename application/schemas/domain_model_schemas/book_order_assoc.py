from uuid import UUID

from pydantic import BaseModel, Field


class BookOrderAssocS(BaseModel):
    order_id: int | None = None
    book_id: UUID | None = None
    count_ordered: int | None = Field(default=None, ge=1)