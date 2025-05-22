from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import database
from app.routers.post import router as post_router


@asynccontextmanager  # Context manager does the setup and the teardown and executes something in the middle which in this case is the app. It does not execute the teardown until the app is stopped either by an error, or manual stop, etc
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(post_router, prefix="/api")
