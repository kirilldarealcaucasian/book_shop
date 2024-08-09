from pydantic import BaseModel


class PaymentDetailS(BaseModel):
    order_id: int | None
    status: str | None
    payment_provider: str | None
    amount: float | None