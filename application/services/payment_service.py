from typing import Protocol


class PaymentServiceInterface(Protocol):

    def create_payment(self):
        pass

    def get_partial_payment_acceptance(self):
        pass