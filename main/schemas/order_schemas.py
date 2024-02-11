from .base_schemas import OrderBaseS, Id


class CreateOrderS(OrderBaseS):
    pass


class UpdateOrderS(OrderBaseS):
    pass


class ReturnOrderS(OrderBaseS, Id):
    pass