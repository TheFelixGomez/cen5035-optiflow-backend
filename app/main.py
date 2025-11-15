from fastapi import FastAPI
from app.routers import vendors_router, orders_router, calendar_router, reporting_router
from app.database import users_collection

app = FastAPI()

app.include_router(vendors_router.router)
app.include_router(orders_router.router)
app.include_router(calendar_router.router)
app.include_router(reporting_router.router)

@app.get("/ping")
def ping():
    return {"message":"pong"}


@app.get("/db-ping")
async def db_ping():
    await users_collection.find_one({})
    return {"message":"db pong"}
