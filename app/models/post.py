from pydantic import BaseModel


class UserPostIn(BaseModel):
    """Types input for post endpoints"""

    body: str


class UserPost(UserPostIn):
    """Types output for post endpoints"""

    id: int
    user_id: int  # When a post is fetched, this relates it to the user whose created it

    class Config:
        orm_mode = True


class CommentIn(BaseModel):
    """Types input for comment endpoints"""

    body: str
    post_id: int


class Comment(CommentIn):
    """Types output for comment endpoints"""

    id: int
    user_id: (
        int  # When a comment is fetched, this relates it to the user whose created it
    )

    class Config:
        # This tells pydantic the objects returned from the database that come from this class must be treated as objects, not as dictionaries. For example cannot be accessed as foo["value"] but as foo.value
        orm_mode = True


class UserPostWithComments(BaseModel):
    """Types output for post with comments endpoints"""

    post: UserPost
    comments: list[Comment]
