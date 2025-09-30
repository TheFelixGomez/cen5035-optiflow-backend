from fastapi import FastAPI

from app.database import users_collection

app = FastAPI()


@app.get("/ping")
def ping():
    return "pong"


@app.get("/db-ping")
async def db_ping():
    await users_collection.find_one({})

    return "db pong"
