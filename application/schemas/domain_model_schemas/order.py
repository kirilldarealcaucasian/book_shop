from datetime import datetime
from pydantic import BaseModel


class OrderS(BaseModel):
    user_id: int | None
    order_status: str | None
    order_date: datetime | None
    total_sum: float | None
    payment_id: str | None