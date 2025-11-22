from fastapi import APIRouter, HTTPException, Path
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


# ---------- ROUTES ----------

@router.get("/", response_model=List[Product])
async def read_products():
    """Get all products."""
    return await get_all_products()


@router.get("/{product_id}", response_model=Product)
async def read_product(product_id: int = Path(..., description="ID of the product to retrieve")):
    """Get a single product by ID."""
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=Product)
async def add_product(product: Product):
    """Create a new product."""
    return await create_product(product)


@router.put("/{product_id}", response_model=Product)
async def modify_product(
    product_id: int = Path(..., description="ID of the product to update"),
    product: Product = ...
):
    """Update an existing product."""
    updated = await update_product(product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}")
async def remove_product(product_id: int = Path(..., description="ID of the product to delete")):
    """Delete a product by ID."""
    deleted = await delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully", "deleted": deleted}