from datetime import datetime
from typing import Annotated, List
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from app.database import orders_collection, vendors_collection
from app.auth.service import get_current_active_user
from app.orders.models import OrderCreate, OrderUpdate, OrderResponse
from app.users.models import User

router = APIRouter(prefix="/orders", tags=["Orders"])

# ---------- Helpers ----------
def validate_object_id(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    return ObjectId(id)


def serialize_order(order) -> dict:
    order_date = order.get("order_date")
    if isinstance(order_date, datetime):
        order_date = order_date.isoformat()
    return {
        "id": str(order["_id"]),
        "vendor_id": str(order["vendor_id"]),
        "user_id": str(order.get("user_id", "")),
        "order_date": order_date,
        "items": order["items"],
        "status": order["status"],
        "total_amount": order.get("total_amount", 0),
        "special_instructions": order.get("special_instructions"),
        "due_at": order.get("due_at"),
    }


# ---------- CREATE ORDER ----------
@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate, current_user: Annotated[User, Depends(get_current_active_user)]
):
    vendor_id = validate_object_id(order.vendor_id)
    vendor = await vendors_collection.find_one({"_id": vendor_id})
    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor does not exist")

    total = sum(item.price * item.quantity for item in order.items)
    order_dict = order.model_dump()
    order_dict["user_id"] = str(current_user.id)
    order_dict["vendor_id"] = vendor_id
    order_dict["total_amount"] = total

    result = await orders_collection.insert_one(order_dict)
    new_order = await orders_collection.find_one({"_id": result.inserted_id})
    return serialize_order(new_order)


# ---------- GET ORDERS ----------
@router.get("/", response_model=List[OrderResponse])
async def get_orders(current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.role == "admin":
        query = {}
    else:
        user_identifier = str(current_user.id) if current_user.id else None
        possible_ids = [value for value in [user_identifier, current_user.username] if value]
        query = {"user_id": {"$in": possible_ids}} if possible_ids else {"user_id": ""}
    orders = await orders_collection.find(query).to_list(length=None)
    return [serialize_order(order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str, current_user: Annotated[User, Depends(get_current_active_user)]
):
    oid = validate_object_id(order_id)
    order = await orders_collection.find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and order.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return serialize_order(order)


# ---------- UPDATE ORDER ----------
@router.put("/{order_id}")
async def update_order(
    order_id: str,
    updated: OrderUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    oid = validate_object_id(order_id)
    existing = await orders_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and existing.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    update_dict = {k: v for k, v in updated.model_dump(exclude_none=True).items()}
    if "items" in update_dict:
        update_dict["total_amount"] = sum(item.price * item.quantity for item in update_dict["items"])

    await orders_collection.update_one({"_id": oid}, {"$set": update_dict})
    updated_order = await orders_collection.find_one({"_id": oid})
    return serialize_order(updated_order)


# ---------- DELETE ORDER ----------
@router.delete("/{order_id}")
async def delete_order(
    order_id: str, current_user: Annotated[User, Depends(get_current_active_user)]
):
    oid = validate_object_id(order_id)
    existing = await orders_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and existing.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    await orders_collection.delete_one({"_id": oid})
    return {"message": "Order deleted successfully"}
