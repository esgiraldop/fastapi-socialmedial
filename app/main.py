import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from app.database import database
from app.logging_conf import configure_logging
from app.routers.post import router as post_router
from app.routers.user import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager  # Context manager does the setup and the teardown and executes something in the middle which in this case is the app. It does not execute the teardown until the app is stopped either by an error, or manual stop, etc
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Hello world")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CorrelationIdMiddleware
)  # To identify in the logs what operation belongs to what user
app.include_router(post_router, prefix="/api")
app.include_router(user_router, prefix="/api")


# This is equivalent to a exception filter in nestjs
@app.exception_handler(HTTPException)
async def http_exception_handle_logger(request, exc):
    # Here, we are basically intercepting the response in case of any error to log the error
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)
