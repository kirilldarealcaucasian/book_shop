from pydantic import BaseModel


class AuthorS(BaseModel):
    first_name: str | None
    last_name: str | None
    book_id: str | None
