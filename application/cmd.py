import time
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import aioredis
from auth.routers import auth_router
from application.api.rest.v1 import (
    image_router,
    order_router, book_router, user_router,
    publisher_router, author_router, cart_router
)
from core.config import settings
from logger import logger
from sqlalchemy import MetaData
# from infrastructure.rabbitmq.connector import rabbit_connector

redis = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis
    if not redis:
        try:
            redis = aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True)
            yield
            logger.info("Shutting down . . .")
            # rabbit_connector.close_con()
            # rabbit_connector.create_chan()
            await redis.close()
        except aioredis.exceptions.ConnectionError as e:
            yield None
        except ConnectionResetError as e:
            yield None

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["8"]
)

for router in (
        book_router, order_router,
        user_router, image_router, auth_router,
        publisher_router, author_router, cart_router
):
    app.include_router(router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info("Request execution time: ", extra={
        "request_process_time": round(process_time, 3)
    })
    return response


@app.get("/")
def home():
    return {"message": "Heeeeeey!"}


if __name__ == "__main__":
    uvicorn.run("application.cmd:app", reload=True)
