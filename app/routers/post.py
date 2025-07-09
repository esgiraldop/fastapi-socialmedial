import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.database import comments_table, database, post_table
from app.models.post import (
    Comment,
    CommentIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)
from app.models.user import User
from app.security import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info(f"Finding posts with id {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


@router.get("/")
async def root():
    return {"message": "Hello world"}


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, user: Annotated[User, Depends(get_current_user)]
):
    # _: User = await get_current_user(
    #     await oauth2_scheme(request)
    # )  # Only authenticated users can access to this endpoint. This line is no longer needed since it was replaced by its dependency injection version with "Depends(get_current_user)" added in the function signature
    logger.info("Creating post")
    data = {
        **post.model_dump(),
        "user_id": user.id,
    }  # The created post is returned with the user who created it
    query = post_table.insert().values(
        data
    )  # The keys of the dictionary must match the column names
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    logger.info("Getting all posts")
    query = post_table.select()

    logger.debug(query)  # For debugging queries

    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn,
    user: Annotated[
        User, Depends(get_current_user)
    ],  # Only authenticated users can access to this endpoint
):
    # _: User = await get_current_user(
    #     await oauth2_scheme(request)
    # )  # Only authenticated users can access to this endpoint. This line is no longer needed since it was replaced by its dependency injection version with "Depends(get_current_user)" added in the function signature
    logger.info("Creating a comment")
    post = await find_post(comment.post_id)
    if not post:
        # logger.error(f"Post with id {comment.post_id} not found") # replaced with the exception handler "http_exception_handle_logger"
        raise HTTPException(status_code=404, detail="Post not found")

    data = {
        "body": comment.body,
        "post_id": comment.post_id,
        "user_id": user.id,
    }  # The created comment is returned with the user who created it
    query = comments_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info(f"Getting comments on post with id {post_id}")
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info(f"Getting post with id {post_id} and its comments")
    post = await find_post(post_id)
    if not post:
        # logger.error(f"Post with id {post_id} not found") # replaced with the exception handler "http_exception_handle_logger"
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }
