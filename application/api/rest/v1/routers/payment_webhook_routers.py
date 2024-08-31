# from fastapi import APIRouter
# from fastapi.requests import Request
# from fastapi.responses import Response
#
#
# router = APIRouter(prefix="", tags=["WebHook"])
#
#
# @router.post("/webhook")
# async def receive_webhook(request: Request):
#     result = await request.json()
#     print(result)
#     return Response(status_code=200)


"""
I init a celery scheduled task (I'll pass cart_id in it)
celery task will use PaymentService to check status of the payment
if status == success, then I clear cart and add data to the order
"""
