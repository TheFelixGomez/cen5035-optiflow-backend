from fastapi import FastAPI

from app.database import users_collection
from app.auth.router import router as auth_router
from app.users.router import router as users_router

app = FastAPI()

app.include_router(users_router)
app.include_router(auth_router)


@app.get("/ping")
def ping():
    return "pong"


@app.get("/db-ping")
async def db_ping():
    await users_collection.find_one({})

    return "db pong"
