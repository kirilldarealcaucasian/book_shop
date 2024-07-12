from main.schemas.base_schemas import ImageBaseS


class ReturnImageS(ImageBaseS):
    id: int
    book_isbn: str
    url: str


class CreateImageS(ImageBaseS):
    book_id: str
    url: str