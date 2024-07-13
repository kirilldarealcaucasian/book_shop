__all__ = (
    "image_router",
    "order_router",
    "book_router",
    "user_router",
    "author_router",
    "publisher_router",
)

from application.api.rest.v1.routers import (
    image_router,
    order_router,
    book_router,
    user_router,
    author_router,
    publisher_router
)