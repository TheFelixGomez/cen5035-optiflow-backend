from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.service import get_current_active_user, get_password_hash
from app.users.models import User, UserCreate, UserDB
from app.users.service import get_user, store_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    existing_user = await get_user(username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_password = get_password_hash(user.password)
    user_dict = user.model_dump()

    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]

    return await store_user(UserDB(**user_dict))


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
