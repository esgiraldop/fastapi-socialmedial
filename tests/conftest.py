import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

"""
Overwritting the environment variable to load the test config, in which the database roll backs the transactions once the test is finished. This is done with variable "DB_FORCE_ROLL_BACK = true"

The env variable must be overwritten before loading the app, which imports the database and then the config. 
"""
os.environ["ENV_STATE"] = "test"  # noqa: E402

from app.database import database, user_table  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(
    scope="session"
)  # Session initializes the variable once every test is run
def anyio_backend():
    "Initializes an async platform for async fast api to run. pytest-asyncio specifically looks for a fixture named anyio_backend and interprets its returned string value as the desired asynchronous backend"
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    ## Method equivalent to the one returning the function directly
    # with TestClient(app, base_url="http://testserver/api") as c:
    #     yield c
    yield TestClient(
        app, base_url="http://testserver/api/"
    )  # "yield" because some teardown code must be executed after using the client for returning it to its original state. Teardown code: Same as cleanup code. Used to revert any changes made during the setup or the test itself, ensuring that subsequent tests start in a clean and predictable state.


@pytest.fixture(
    autouse=True
)  # Autouse for running the fixture BEFORE EVERY test defined in the context (test module or conftest), so there is no need to pass it as an argument to the tests. So in this case, the post and comment tables are cleaned up before every test begins.
async def db() -> AsyncGenerator:
    await (
        database.connect()
    )  # Thanks to the "autouse", the database is connected before any test begin
    yield
    await database.disconnect()  # Teardown


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with (
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url=client.base_url,  # "ASGITransport" is a httpx plugin to run httpx clients asyncronously --> https://fastapi.tiangolo.com/advanced/async-tests/
        ) as ac
    ):
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    """Fixture to register a user"""
    user_details = {"email": "test@example.net", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details
