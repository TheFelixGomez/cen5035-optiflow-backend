from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from bson import ObjectId

from bson import ObjectId

from app.auth.service import get_current_active_user, get_password_hash
from app.users.models import User, UserCreate, UserDB, UserUpdate
from app.users.service import get_user, store_user
from app.database import users_collection
from app.database import users_collection

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# ---------- Helpers ----------
def user_to_model(user_doc: dict) -> User:
    """Convert MongoDB document to User Pydantic model."""
    return User(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        role=user_doc.get("role", "customer"),
        disabled=user_doc.get("disabled", False),
    )


def validate_object_id(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    return ObjectId(id)


# ---------- Routes ----------
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    existing_user = await get_user(username=user.username)
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
    user_dict["role"] = user_dict.get("role", "customer")
    user_dict.pop("password", None)

    result = await users_collection.insert_one(user_dict)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )
    return user_to_model(created_user)


@router.get("/", response_model=list[User])
async def list_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    users = await users_collection.find({}).to_list(length=None)
    return [user_to_model(user) for user in users]


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    # current_user is already a UserDB model from auth, convert to User response
    user_doc = await users_collection.find_one({"username": current_user.username})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_model(user_doc)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    oid = validate_object_id(user_id)
    existing = await users_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = {k: v for k, v in user_update.model_dump(exclude_none=True).items()}
    if update_dict:
        await users_collection.update_one({"_id": oid}, {"$set": update_dict})

    updated_user = await users_collection.find_one({"_id": oid})
    return user_to_model(updated_user)


@router.get("/exists")
async def check_user_exists(email: str):
    user = await users_collection.find_one({"username": email})
    user = await users_collection.find_one({"username": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"exists": True}



@router.get("/count")
async def get_users_count():
    count = await users_collection.count_documents({})
    return {"count": count}
