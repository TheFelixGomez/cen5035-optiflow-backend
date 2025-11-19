from fastapi import APIRouter, HTTPException
from typing import List

from app.products.models import Product
from app.products.service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
)

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=List[Product])
async def read_products():
    return await get_all_products()


@router.get("/{product_id}", response_model=Product)
async def read_product(product_id: int):
    product = await get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=Product)
async def add_product(product: Product):
    return await create_product(product)


@router.put("/{product_id}", response_model=Product)
async def modify_product(product_id: int, product: Product):
    return await update_product(product_id, product)


@router.delete("/{product_id}")
async def remove_product(product_id: int):
    deleted = await delete_product(product_id)
    return {
        "message": "Product deleted" if deleted else "Product not found",
        "deleted": deleted,
    }
