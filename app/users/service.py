from app.database import users_collection
from app.users.models import User, UserDB


async def get_user(username: str):
    user = await users_collection.find_one({"username": username})
    if user:
        mongo_id = user.get("_id")
        if mongo_id is not None:
            user["_id"] = str(mongo_id)
            user["id"] = str(mongo_id)
        return UserDB(**user)
    return None


async def store_user(user: UserDB) -> User | None:
    user_created = await users_collection.insert_one(user.model_dump())
    if user_created.acknowledged:
        return User(
            **user.model_dump(),
            _id=str(user_created.inserted_id),
        )
    return None
