from .base_schemas import ImageBaseS


class ReturnImageS(ImageBaseS):
    id: int
    product_id: int
    url: str


class CreateImageS(ImageBaseS):
    product_id: int
    url: str