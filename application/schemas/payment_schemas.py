from pydantic import BaseModel, Field, EmailStr

from application.schemas import OrderItemS


class CreateReceiptS(BaseModel):
    customer_full_name: str = Field(min_length=3)
    customer_email: EmailStr
    items: list[OrderItemS]


class CreatePaymentS(BaseModel):
    total_amount: float = Field(ge=1.0)
    currency: str = Field(default="RUB", min_length=2)
    description: str
    receipt: CreateReceiptS


class ReturnPaymentS(BaseModel):
    confirmation_url: str
    payment_id: str






