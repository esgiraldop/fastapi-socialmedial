from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    id: int

    class Config:
        orm_mode = True


class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    id: int

    class Config:
        # This tells pydantic the objects returned from the database that come from this class must be treated as objects, not as dictionaries. For example cannot be accessed as foo["value"] but as foo.value
        orm_mode = True


class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[Comment]
