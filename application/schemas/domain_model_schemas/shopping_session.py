from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ShoppingSessionS(BaseModel):
    id: UUID | None
    user_id: int | None
    total: float | None
    expiration_time: datetime | None
    created_at: datetime | None
    updated_at: datetime | None