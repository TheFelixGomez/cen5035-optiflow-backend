from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import reporting_router
from app.database import users_collection
from app.auth import router as auth_router
from app.users import router as users_router
from app.orders import router as orders_router
from app.calendar import router as calendar_router
from app.vendors import router as vendors_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # All origins allowed for simplicity (we ignore security on purpose)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(vendors_router.router)
app.include_router(orders_router.router)
app.include_router(calendar_router.router)
app.include_router(reporting_router.router)


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get("/db-ping")
async def db_ping():
    await users_collection.find_one({})
    return {"message":"db pong"}
