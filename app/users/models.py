from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class User(BaseModel):
    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

    id: str | None = Field(default=None, alias="_id", serialization_alias="id")
    username: str
    disabled: bool = False
    role: str = "customer"


class UserDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "customer"


class UserUpdate(BaseModel):
    role: str | None = None
    disabled: bool | None = None 
