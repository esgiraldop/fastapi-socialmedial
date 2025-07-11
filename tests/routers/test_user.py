import pytest
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "/register", json={"email": email, "password": password}
    )


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.net", "1234")
    assert response.status_code == 201
    assert "User created" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_exists(
    async_client: AsyncClient, registered_user: dict
):
    response = await register_user(
        async_client, registered_user["email"], registered_user["password"]
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/login", json={"email": "test@example.com", "password": "1234"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 201
    assert "bearer" == response.json()["token_type"]
