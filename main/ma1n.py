from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import routers.product_routers, \
    routers.category_routers, \
    routers.order_routers, \
    routers.image_routers, \
    routers.user_routers, \
    routers.order_product_routers
import aioredis
from auth.routers.auth_routers import router as auth_router


redis = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis
    if not redis:
        try:
            redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)
            yield
            redis.close()
        except aioredis.exceptions.ConnectionError as e:
            yield None
        except ConnectionResetError as e:
            yield None


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), "static")

app.include_router(routers.product_routers.router)
app.include_router(routers.category_routers.router)
app.include_router(routers.order_routers.router)
app.include_router(routers.user_routers.router)
app.include_router(auth_router)
app.include_router(routers.order_product_routers.router)
app.include_router(routers.image_routers.router)


@app.get("/")
def home():
    return {"message": "Heeeeeey!"}


if __name__ == "__main__":
    uvicorn.run("main.ma1n:app", reload=True)
