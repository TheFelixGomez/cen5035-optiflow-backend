from typing import List, Optional
from app.models import Product
from app.database import products_collection
from pymongo import UpdateOne
import asyncio

class ProductService:
    @staticmethod
    async def get_all_products() -> List[Product]:
        cursor = products_collection.find({})
        products = await cursor.to_list(length=None)
        return [Product(**p) for p in products]

    @staticmethod
    async def get_product_by_id(product_id: int) -> Optional[Product]:
        doc = await products_collection.find_one({"id": product_id})
        return Product(**doc) if doc else None


    @staticmethod
    async def create_product(product: Product) -> Product:
        await products_collection.insert_one(product.dict())
        return product

    @staticmethod
    async def update_product(product_id: int, updated_product: Product) -> Optional[Product]:
        result = await products_collection.update_one(
            {"id": product_id},
            {"$set": updated_product.dict()}
        )
        return updated_product if result.matched_count > 0 else None


    @staticmethod
    async def delete_product(product_id: int) -> bool:
        result = await products_collection.delete_one({"id": product_id})
        return result.deleted_count > 0