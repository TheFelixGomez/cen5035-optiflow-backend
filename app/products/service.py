from typing import List, Optional

from app.database import products_collection
from app.products.models import Product


async def get_all_products() -> List[Product]:
    cursor = products_collection.find({})
    products = await cursor.to_list(length=None)

    # Convert MongoDB docs into Product models
    return [Product(**p) for p in products]


async def get_product_by_id(product_id: int) -> Optional[Product]:
    doc = await products_collection.find_one({"id": product_id})
    return Product(**doc) if doc else None


async def create_product(product: Product) -> Product:
    # Convert Pydantic model into MongoDB-safe dict
    product_dict = product.model_dump(mode="json")

    # Remove internal _id if present to avoid conflicts
    product_dict.pop("_id", None)

    await products_collection.insert_one(product_dict)

    return Product(**product_dict)


async def update_product(
    product_id: int, updated_product: Product
) -> Optional[Product]:

    # Serialize safely
    updated_dict = updated_product.model_dump(mode="json")
    updated_dict.pop("_id", None)

    result = await products_collection.update_one(
        {"id": product_id},
        {"$set": updated_dict}
    )

    return updated_product if result.matched_count > 0 else None


async def delete_product(product_id: int) -> bool:
    result = await products_collection.delete_one({"id": product_id})
    return result.deleted_count > 0
