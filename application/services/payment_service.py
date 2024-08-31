import asyncio
import json
from typing import Protocol, TypeAlias
from yookassa import Payment, Configuration
from uuid import uuid4

from application.schemas import CreatePaymentS, ReturnPaymentS
from core.config import settings


__all__ = (
    "PaymentServiceInterface",
    "YooCassaPaymentService"
)

from core.exceptions import PaymentObjectCreationError, PaymentRetrieveStatusError
from logger import logger

PaymentID: TypeAlias = str


class PaymentServiceInterface(Protocol):

    def create_payment(
            self,
            payment_data: CreatePaymentS
    ) -> ReturnPaymentS:
        ...

    def get_payment_status(self, payment_status: int) -> str:
        ...

    async def check_payment_status(self, payment_id: str) -> bool:
        ...


class YooCassaPaymentService:

    def __init__(self):
        Configuration.account_id = settings.YOOCASSA_ACCOUNT_ID
        Configuration.secret_key = settings.YOOCASSA_SECRET_KEY

    def create_payment(
            self,
            payment_data: CreatePaymentS
    ) -> ReturnPaymentS:
        idempotancy_key = uuid4()

        try:
            payment = Payment.create(
                {
                    "amount": {
                        "value": payment_data.total_amount,
                        "currency": payment_data.currency
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": "http://127.0.0.1:8000"
                    },
                    "capture": True,
                    "description": payment_data.description,
                    "metadata": {
                    },
                },
                idempotency_key=idempotancy_key
            )  # create Payment object
        except (TypeError, ValueError):
            extra = {
                "payment_data": payment_data
            }
            logger.error(
                "Failed to create payment object",
                exc_info=True, extra=extra
            )
            raise PaymentObjectCreationError()

        payment_data = json.loads(payment.json())

        payment_id = payment_data["id"]
        confirmation_url = payment_data["confirmation"]["confirmation_url"]
        return ReturnPaymentS(
            confirmation_url=confirmation_url,
            payment_id=payment_id
        )

    def get_payment_status(self, payment_id: PaymentID) -> str:
        try:
            payment = json.loads(Payment.find_one(payment_id).json())
            return payment["status"]
        except Exception:
            logger.error(
                "Failed to get payment_status",
                exc_info=True,
                extra={"payment_id": payment_id}
            )
            raise PaymentRetrieveStatusError()

    async def check_payment_status(self, payment_id: str) -> bool:
        payment_status = self.get_payment_status(payment_id=payment_id)

        while payment_status == "pending":
            payment_status = self.get_payment_status(payment_id=payment_id)
            await asyncio.sleep(5)

        if payment_status == "succeeded":
            return True

        else:
            return False