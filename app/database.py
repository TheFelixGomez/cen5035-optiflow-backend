from decouple import config
from pymongo import AsyncMongoClient

client = AsyncMongoClient(config("MONGODB_URL").strip('"'))

# Access to Optiflow MongoDB
mongo_db = client.optiflow

# Access to all collections on Optiflow MongoDB
users_collection = mongo_db.users
orders_collection = mongo_db.orders
vendors_collection = mongo_db.vendors
products_collection = mongo_db.products

