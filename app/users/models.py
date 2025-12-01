from pydantic import BaseModel, Field

class User(BaseModel):
    id: str
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
