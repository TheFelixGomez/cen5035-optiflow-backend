from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from bson import ObjectId

from app.auth.service import get_current_active_user, get_password_hash
from app.users.models import User, UserCreate, UserDB
from app.users.service import get_user, store_user
from app.database import users_collection

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# ---------- Helpers ----------
def user_serializer(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "customer"),
        "disabled": user.get("disabled", False),
    }


def validate_object_id(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    return ObjectId(id)


# ---------- Routes ----------
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
    user_dict["role"] = user_dict.get("role", "customer")
    user_dict.pop("password", None)

    created_user = await store_user(UserDB(**user_dict))
    if created_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )
    return user_serializer(created_user)


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return user_serializer(current_user)


@router.get("/exists")
async def check_user_exists(email: str):
    user = await users_collection.find_one({"username": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"exists": True}


@router.get("/count")
async def get_users_count():
    count = await users_collection.count_documents({})
    return {"count": count}
