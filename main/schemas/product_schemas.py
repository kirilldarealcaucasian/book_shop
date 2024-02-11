from .base_schemas import ProductBaseS, Id
from pydantic import BaseModel


class ReturnProductS(ProductBaseS, Id):
    category_id: int | None


class CreateProductS(ProductBaseS):
    pass


class UpdateProductS(ProductBaseS):
    image_id: int | None = None
    category_id: int | None = None



class UpdatePartiallyProductS(BaseModel):
    name: str | None = None
    description: str | None = None
    price_per_unit: int | None = None
    number_in_stock: int | None = None
    category_id: int | None = None
