from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database import orders_collection, users_collection
from app.models import Order

router = APIRouter(prefix="/orders", tags=["Orders"])

def order_serializer(order) -> dict:
    return {
        "id": str(order["_id"]),
        "vendor_id": str(order["vendor_id"]),
        "order_date": str(order["order_date"]),
        "items": order["items"],
        "status": order["status"],
        "total_amount": order.get("total_amount", 0),
    }

@router.post("/")
async def create_order(order: Order):
    vendor = await users_collection.find_one({"_id": ObjectId(order.vendor_id)})
    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor does not exist")

    total = sum(item.price * item.quantity for item in order.items)
    order_dict = order.model_dump()
    order_dict["total_amount"] = total

    result = await orders_collection.insert_one(order_dict)
    order_dict["_id"] = str(result.inserted_id)
    return order_dict

@router.get("/")
async def get_orders():
    orders = []
    async for order in orders_collection.find():
        order["_id"] = str(order["_id"])
        orders.append(order)
    return orders

@router.get("/{order_id}")
async def get_order(order_id: str):
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order["_id"] = str(order["_id"])
    return order

@router.put("/{order_id}")
async def update_order(order_id: str, updated_order: Order):
    updated_dict = updated_order.model_dump()
    updated_dict["total_amount"] = sum(item.price * item.quantity for item in updated_order.items)

    result = await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": updated_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order updated successfully"}

@router.delete("/{order_id}")
async def delete_order(order_id: str):
    result = await orders_collection.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}