from typing import Annotated

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Depends

from app.database import orders_collection, users_collection
from app.auth.service import get_current_active_user
from app.orders.models import OrderResponse, OrderCreate
from app.orders.service import serialize_order
from app.users.models import User

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate, current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        vendor_obj_id = ObjectId(order.vendor_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid vendor ID format")

    vendor_exists = await users_collection.find_one({"_id": vendor_obj_id})
    if not vendor_exists:
        raise HTTPException(status_code=400, detail="Vendor does not exist")

    # Calculate total
    total = sum(item.price * item.quantity for item in order.items)

    order_dict = order.model_dump()
    order_dict["user_id"] = str(current_user.id)
    order_dict["vendor_id"] = vendor_obj_id
    order_dict["total_amount"] = total

    result = await orders_collection.insert_one(order_dict)
    new_order = await orders_collection.find_one({"_id": result.inserted_id})

    return serialize_order(new_order)


@router.get("/", response_model=list[OrderResponse])
async def get_orders(current_user: Annotated[User, Depends(get_current_active_user)]):
    query = {} if current_user.role == "admin" else {"user_id": str(current_user.id)}

    data = await orders_collection.find(query).to_list(length=None)
    return [serialize_order(order) for order in data]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str, current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        oid = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    order = await orders_collection.find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Customer cannot access another user's order
    if current_user.role != "admin" and order.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    return serialize_order(order)


@router.put("/{order_id}")
async def update_order(
    order_id: str,
    updated: OrderCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    try:
        oid = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    existing = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")

    # Customer cannot modify another user's order
    if current_user.role != "admin" and existing.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    updated_dict = updated.model_dump()
    updated_dict["total_amount"] = sum(
        item.price * item.quantity for item in updated.items
    )

    result = await orders_collection.update_one({"_id": oid}, {"$set": updated_dict})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order updated successfully"}


@router.delete("/{order_id}")
async def delete_order(
    order_id: str, current_user: Annotated[User, Depends(get_current_active_user)]
):
    try:
        oid = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    existing = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")

    # Customer cannot delete another user's order
    if current_user.role != "admin" and existing.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await orders_collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order deleted successfully"}
