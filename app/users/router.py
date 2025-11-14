from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from app.auth.service import get_current_active_user, get_password_hash
from app.users.models import User, UserCreate, UserDB
from app.users.service import get_user, store_user
from app.database import users_collection  # Directly import the collection

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    existing_user = get_user(username=user.username)  # Remove await
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    hashed_password = get_password_hash(user.password)
    user_dict = user.model_dump()

    if "role" not in user_dict or not user_dict["role"]:
        user_dict["role"] = "customer"

    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]

    created_user = store_user(UserDB(**user_dict))  # Remove await
    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )
    return created_user


@router.get("/me", response_model=User)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/exists")
def check_user_exists(email: str):
    """
    Checks if a user exists by email (username).
    Returns { "exists": True } if found, or 404 if not.
    """
    user = users_collection.find_one({"username": email})  # Remove await
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"exists": True}
