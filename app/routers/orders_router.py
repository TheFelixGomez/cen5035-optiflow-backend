from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from bson import ObjectId
from app.database import orders_collection, users_collection
from app.models import Order
from app.auth.service import get_current_active_user

router = APIRouter(prefix="/orders", tags=["Orders"])


#   CREATE ORDER (customer/admin)
@router.post("/")
async def create_order(
    order: Order,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    # Validate vendor
    vendor = await users_collection.find_one({"_id": ObjectId(order.vendor_id)})
    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor does not exist")

    # Attach the user who creates the order
    order_dict = order.model_dump()
    order_dict["user_id"] = str(current_user.id)

    # Calculate total
    total = sum(item.price * item.quantity for item in order.items)
    order_dict["total_amount"] = total

    # Save in DB
    result = await orders_collection.insert_one(order_dict)
    order_dict["_id"] = str(result.inserted_id)
    return order_dict


#   GET ORDERS 
@router.get("/")
async def get_orders(current_user: Annotated[dict, Depends(get_current_active_user)]):

    query = {} if current_user.role == "admin" else {"user_id": str(current_user.id)}

    orders = []
    async for order in orders_collection.find(query):
        order["_id"] = str(order["_id"])
        orders.append(order)

    return orders



#   GET SINGLE ORDER
@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Customer cannot access another user's order
    if current_user.role != "admin" and order.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    order["_id"] = str(order["_id"])
    return order


#   UPDATE ORDER
@router.put("/{order_id}")
async def update_order(
    order_id: str,
    updated_order: Order,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    existing = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")

    # Customer cannot modify another user's order
    if current_user.role != "admin" and existing.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    updated_dict = updated_order.model_dump()
    updated_dict["total_amount"] = sum(item.price * item.quantity for item in updated_order.items)

    await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": updated_dict}
    )
    return {"message": "Order updated successfully"}


#   DELETE ORDER
@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    current_user: Annotated[dict, Depends(get_current_active_user)]
):
    existing = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")

    # Customer cannot delete another user's order
    if current_user.role != "admin" and existing.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")

    await orders_collection.delete_one({"_id": ObjectId(order_id)})
    return {"message": "Order deleted successfully"}
