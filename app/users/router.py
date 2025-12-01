from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from typing import Annotated

from app.database import users_collection
from app.auth.service import get_current_active_user, get_password_hash
from app.users.models import User, UserCreate, UserUpdate, UserDB

router = APIRouter(prefix="/users", tags=["Users"])


# -----------------------------
# Create new user (open or admin)
# -----------------------------
@router.post("/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    # Check for existing username
    existing = await users_collection.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Prepare data
    user_dict = user.model_dump()
    user_dict["hashed_password"] = get_password_hash(user.password)
    del user_dict["password"]

    result = await users_collection.insert_one(user_dict)

    created_user = {
        "id": str(result.inserted_id),
        "username": user.username,
        "role": user.role,
        "disabled": False,
    }

    return User(**created_user)


# -----------------------------
# Return current logged-in user
# -----------------------------
@router.get("/me", response_model=User)
async def read_me(current_user: Annotated[User, Depends(get_current_active_user)]):

    user_data = await users_collection.find_one({"username": current_user.username})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    user_data["id"] = str(user_data["_id"])
    del user_data["_id"]

    return User(**user_data)


# -----------------------------
# Get user by ID
# -----------------------------
@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: str):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    user_data["id"] = str(user_data["_id"])
    del user_data["_id"]

    return User(**user_data)


# -----------------------------
# Update user (only self or admin)
# -----------------------------
@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # Only admin or the user themselves
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = {k: v for k, v in update.model_dump().items() if v is not None}

    if update_data:
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
        )

    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user["id"] = str(updated_user["_id"])
    del updated_user["_id"]

    return User(**updated_user)


# -----------------------------
# Delete user (admin only)
# -----------------------------
@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = await users_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return None
