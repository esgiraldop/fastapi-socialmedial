from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.routers.post import comment_table, post_table


@pytest.fixture(
    scope="session"
)  # Session initializes the variable once every test is run
def anyio_backend():
    "Initializes an async platform for async fast api to run. pytest-asyncio specifically looks for a fixture named anyio_backend and interprets its returned string value as the desired asynchronous backend"
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(
        app
    )  # "yield" because some teardown code must be executed after using the client for returning it to its original state. Teardown code: Same as cleanup code. Used to revert any changes made during the setup or the test itself, ensuring that subsequent tests start in a clean and predictable state.


@pytest.fixture(
    autouse=True
)  # Autouse for appliying the fixture to all the tests defined in the context (test module or conftest), so there is no need to pass it as an argument to the tests
async def db() -> AsyncGenerator:
    post_table.clear()  # Thanks to the "autouse", the database is cleaned up before any test begin
    comment_table.clear()
    yield


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac
