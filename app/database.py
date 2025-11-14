from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient

# Create async MongoDB client
client = AsyncIOMotorClient(config("MONGODB_URL").strip('"'))

# Access to database
mongo_db = client.optiflow

# Access to collections
users_collection = mongo_db.users
orders_collection = mongo_db.orders
vendors_collection = mongo_db.vendors
products_collection = mongo_db.products

# Dependency for FastAPI: returns DB instance per request
async def get_db():
    return mongo_db


