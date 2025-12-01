from datetime import datetime
from typing import Annotated
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from app.database import orders_collection, vendors_collection
from app.auth.service import get_current_active_user
from app.orders.models import OrderCreate, OrderUpdate, OrderResponse
from app.users.models import User

router = APIRouter(prefix="/orders", tags=["Orders"])

# ---------- Helpers ----------
def validate_object_id(id: str) -> str:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    return id

# ---------- CREATE ORDER ----------
@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    vendor_id = validate_object_id(order.vendor_id)
    vendor = await vendors_collection.find_one({"_id": ObjectId(vendor_id)})
    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor does not exist")

    total = sum(item.price * item.quantity for item in order.items)
    order_dict = order.model_dump()
    order_dict["user_id"] = str(current_user.id)
    order_dict["vendor_id"] = vendor_id
    order_dict["total_amount"] = total

    result = await orders_collection.insert_one(order_dict)
    new_order = await orders_collection.find_one({"_id": result.inserted_id})

    # Convert ObjectId fields to string
    new_order["id"] = str(new_order["_id"])
    new_order["user_id"] = str(new_order["user_id"])
    new_order["vendor_id"] = str(new_order["vendor_id"])

    return OrderResponse(**new_order)

# ---------- GET SINGLE ORDER ----------
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    oid = validate_object_id(order_id)
    order = await orders_collection.find_one({"_id": ObjectId(oid)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != "admin" and order.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    order["id"] = str(order["_id"])
    order["user_id"] = str(order["user_id"])
    order["vendor_id"] = str(order["vendor_id"])

    return OrderResponse(**order)

# ---------- UPDATE ORDER ----------
@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    updated: OrderUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    oid = validate_object_id(order_id)
    existing = await orders_collection.find_one({"_id": ObjectId(oid)})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != "admin" and existing.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    update_dict = updated.model_dump(exclude_none=True)
    if "items" in update_dict:
        update_dict["total_amount"] = sum(item.price * item.quantity for item in update_dict["items"])

    await orders_collection.update_one({"_id": ObjectId(oid)}, {"$set": update_dict})
    updated_order = await orders_collection.find_one({"_id": ObjectId(oid)})

    updated_order["id"] = str(updated_order["_id"])
    updated_order["user_id"] = str(updated_order["user_id"])
    updated_order["vendor_id"] = str(updated_order["vendor_id"])

    return OrderResponse(**updated_order)

# ---------- DELETE ORDER ----------
@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    oid = validate_object_id(order_id)
    existing = await orders_collection.find_one({"_id": ObjectId(oid)})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != "admin" and existing.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    await orders_collection.delete_one({"_id": ObjectId(oid)})
    return {"message": "Order deleted successfully"}
