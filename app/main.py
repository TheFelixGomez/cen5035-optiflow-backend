from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.database import users_collection
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.orders.router import router as orders_router
from app.calendar.router import router as calendar_router
from app.vendors.router import router as vendors_router
from app.reporting.router import router as reporting_router
from app.products.router import router as products_router


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

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(orders_router)
app.include_router(vendors_router)
app.include_router(products_router)
app.include_router(calendar_router)
app.include_router(reporting_router)


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get("/db-ping")
async def db_ping():
    await users_collection.find_one({})
    return {"message":"db pong"}
