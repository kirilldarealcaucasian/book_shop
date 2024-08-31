from yookassa import Configuration, Webhook, Payment
from yookassa.domain.notification import WebhookNotificationEventType

Configuration.configure(
    '383247',
    'test_NLkvayRHYl2yWpOoDUDhzEyYo2o88Pnr_b6tjl2sPOU'
)


# def create_payment():
#     id = uuid.uuid4()
#     payment: Payment = Payment.create({
#         "amount": {
#             "value": "100.00",
#             "currency": "RUB"
#         },
#         "confirmation": {
#             "type": "redirect",
#             "return_url": "https://www.example.com/return_url"
#         },
#         "capture": True,
#         "description": {
#             "Product Description . . ."
#         }
#     }, id)
# # Set up a webhook subscription

whUrl = 'http:127.0.0.1:8000/webhook'

needWebhookList = [
    WebhookNotificationEventType.PAYMENT_SUCCEEDED,
    WebhookNotificationEventType.PAYMENT_CANCELED
]

whList = Webhook.list()

for event in needWebhookList:
    hookIsSet = False
    for wh in whList.items:
        if wh.event != event:
            continue
        if wh.url != whUrl:
            Webhook.remove(wh.id)
        else:
            hookIsSet = True

    if not hookIsSet:
        Webhook.add({"event": event, "url": whUrl})
