import asyncio
from httpx import AsyncClient
from pymongo import UpdateOne
from decouple import config

from app.database import products_collection

FAKESTORE_URL = config("FAKESTORE_URL")

async def fetch_products():
    async with AsyncClient(timeout=30) as client:
        resp = await client.get(FAKESTORE_URL)
        resp.raise_for_status()
        return resp.json()

def transform_product(item: dict) -> dict:
    return {
        "id": int(item.get("id")),
        "title": item.get("title"),
        "price": float(item.get("price")),
        "description": item.get("description"),
        "category": item.get("category"),
        "image": item.get("image"),
        "rating": item.get("rating"),
        "source": "fakestoreapi"
    }

async def create_indexes():
    await products_collection.create_index("id", unique=True)
    await products_collection.create_index("category")

async def migrate():
    print("Fetching products from fakestoreapi...")
    items = await fetch_products()
    if not isinstance(items, list):
        print("Unexpected response format:", items)
        return

    print(f"Fetched {len(items)} products. Transforming...")
    ops = []
    for item in items:
        doc = transform_product(item)
        ops.append(
            UpdateOne(
                {"id": doc["id"]},
                {"$set": doc},
                upsert=True
            )
        )

    if not ops:
        print("No operations to run.")
        return

    print("Creating indexes (if not exist)...")
    await create_indexes()

    print("Running bulk_write (upsert)...")
    result = await products_collection.bulk_write(ops, ordered=False)
    print("Bulk write result:", result.bulk_api_result)

if __name__ == "__main__":
    asyncio.run(migrate())