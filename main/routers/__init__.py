
__all__ = (
    "image_router",
    "order_router",
    "book_router",
    "user_router",
    "author_router",
    "publisher_router",
)


from main.routers.image_routers import router as image_router
from main.routers.order_routers import router as order_router
from main.routers.book_routers import router as book_router
from main.routers.user_routers import router as user_router
from main.routers.author_routers import router as author_router
from main.routers.publisher_routers import router as publisher_router