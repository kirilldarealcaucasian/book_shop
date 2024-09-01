from uuid import UUID

from pydantic import BaseModel, Field


class PaymentDetailS(BaseModel):
    id: UUID | None = None
    order_id: int | None = None
    status: str | None = Field(default="pending")
    payment_provider: str | None = None
    amount: float | None = None