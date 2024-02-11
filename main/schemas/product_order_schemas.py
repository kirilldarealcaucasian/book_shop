from pydantic import BaseModel


class AssocProductS(BaseModel):
    name: str
    price_per_unit: int
    number_in_stock: int
    count_ordered: int


class ReturnOrderProductS(BaseModel):
    products: list[AssocProductS]


class ReturnOrderIdProductS(ReturnOrderProductS):
    order_id: int
