from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from app.database import orders_collection, users_collection
from app.models import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


def serialize_order(order) -> dict:
    return {
        "id": str(order["_id"]),
        "vendor_id": str(order["vendor_id"]),
        "order_date": str(order["order_date"]),
        "items": order["items"],
        "status": order["status"],
        "total_amount": order.get("total_amount", 0),
        "special_instructions": order.get("special_instructions"),
        "due_at": str(order.get("due_at")) if order.get("due_at") else None,
    }

#Create Order
@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate):
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
    order_dict["vendor_id"] = vendor_obj_id
    order_dict["total_amount"] = total

    result = await orders_collection.insert_one(order_dict)
    new_order = await orders_collection.find_one({"_id": result.inserted_id})

    return serialize_order(new_order)

# Get All Orders
@router.get("/", response_model=list[OrderResponse])
async def get_orders():
    data = await orders_collection.find().to_list(length=None)
    return [serialize_order(order) for order in data]

# Get One Order
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    try:
        oid = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    order = await orders_collection.find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return serialize_order(order)

# Update Order
@router.put("/{order_id}")
async def update_order(order_id: str, updated: OrderCreate):
    try:
        oid = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    updated_dict = updated.model_dump()
    updated_dict["total_amount"] = sum(item.price * item.quantity for item in updated.items)

    result = await orders_collection.update_one(
        {"_id": oid},
        {"$set": updated_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order updated successfully"}

# Delete Order
@router.delete("/{order_id}")
async def delete_order(order_id: str):
    try:
        oid = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid order ID")

    result = await orders_collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order deleted successfully"}