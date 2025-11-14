from decouple import config
from pymongo import MongoClient

# Create MongoDB client
client = MongoClient(config("MONGODB_URL").strip('"'))

# Access to database
mongo_db = client["optiflow"]

# Access to collections
users_collection = mongo_db["users"]
orders_collection = mongo_db["orders"]
vendors_collection = mongo_db["vendors"]
products_collection = mongo_db["products"]

# Dependency for FastAPI: returns DB instance per request
def get_db():
    return mongo_db


