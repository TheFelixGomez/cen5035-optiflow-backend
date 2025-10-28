from fastapi import FastAPI
#from app.database import users_collection
from app.routers import products 

app = FastAPI(title="OptiFlow API")

app.include_router(products.router, prefix="/products", tags=["Products"])

@app.get("/ping")
def ping():
    return {"message": "pong"}