from pydantic import BaseModel


class User(BaseModel):
    # As we do not want to return the password, we leave the class including the password in class UserIn
    id: int | None = None
    email: str


class UserIn(User):
    password: str
