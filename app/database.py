from decouple import config
from pymongo import AsyncMongoClient

client = AsyncMongoClient(config("MONGODB_URL").strip('"'))

# Access to optiflow MongoDB
mongo_db = client.optiflow

# Access to each all collections on optiflow MongoDB
users_collection = mongo_db.users
