from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class User(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    username: str
    disabled: bool = False


class UserDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    password: str
    