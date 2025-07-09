import pytest
from httpx import AsyncClient

from app import security


async def create_post(
    body: str, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/post",
        json={"body": body},
        headers={
            "Authorization": f"Bearer {logged_in_token}"
        },  # This token is grabbed from the request by security.oauth2_scheme in the controller
    )
    return response.json()


async def create_comment(
    body: str, post_id: int, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/comment",
        json={
            "body": body,
            "post_id": post_id,
        },
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    """Fixture of a created post"""
    return await create_post("Test post", async_client, logged_in_token)


@pytest.fixture()
async def created_comment(
    async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    """Fixture of a created comment"""
    return await create_comment(
        "Test comment", created_post["id"], async_client, logged_in_token
    )


@pytest.mark.anyio  # Telling pytest this test should use the async backend configured in the conftest
async def test_create_post(
    async_client: AsyncClient, registered_user: dict, logged_in_token: str
):
    body = "Test Post"

    response = await async_client.post(
        "/post",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 201
    assert (
        {"id": 1, "body": body, "user_id": registered_user["id"]}.items()
        <= response.json().items()
    )  # "<=" for assessing the expression at the left is included in the one at the right


@pytest.mark.anyio
async def test_create_post_no_body(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.post(
        "/post", headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    assert response.status_code == 422
    assert {
        "type": "missing",
        "loc": ["body"],
        "msg": "Field required",
        "input": None,
    }.items() <= response.json()["detail"][0].items()


@pytest.mark.anyio
async def test_create_post_expire_token(
    async_client: AsyncClient, registered_user: dict, mocker
):
    mocker.patch("app.security.access_token_expire_minutes", return_value=-1)
    token = security.create_access_token(registered_user["email"])
    response = await async_client.post(
        "/post",
        json={"body": "Test Post"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]


@pytest.mark.anyio
async def test_get_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post")

    assert response.status_code == 200
    assert created_post in response.json()


@pytest.mark.anyio
async def test_create_comment(
    async_client: AsyncClient, created_post, registered_user: dict, logged_in_token: str
):
    body = "Test comment"
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": 1},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 201

    assert {
        "body": body,
        "post_id": created_post["id"],
        "user_id": registered_user["id"],
        # "id":
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_comment_no_post(async_client: AsyncClient, logged_in_token: str):
    body = "Test comment"
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": 1},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_comments(async_client: AsyncClient, created_comment):
    response = await async_client.get("/post/1/comments")
    assert response.status_code == 200
    assert created_comment in response.json()


@pytest.mark.anyio
async def test_get_comments_no_comment(async_client: AsyncClient):
    response = await async_client.get("/post/0/comments")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post, created_comment
):
    response = await async_client.get(f"/post/{created_post['id']}")

    assert response.status_code == 200
    assert {
        "post": created_post,
        "comments": [created_comment],
    }.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_post_with_comments_when_post_doesn_exist(async_client: AsyncClient):
    response = await async_client.get("/post/0")

    assert response.status_code == 404
