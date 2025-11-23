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
    return {
        "id": str(order["_id"]),
        "vendor_id": str(order["vendor_id"]),
        "user_id": str(order.get("user_id", "")),
        "order_date": str(order["order_date"]),
        "items": order["items"],
        "status": order["status"],
        "total_amount": order.get("total_amount", 0),
        "special_instructions": order.get("special_instructions"),
        "due_at": order.get("due_at"),
    }


# ---------- CREATE ORDER ----------
@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    vendor_id = validate_object_id(order.vendor_id)
    vendor = await vendors_collection.find_one({"_id": vendor_id})
    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor does not exist")

    total = sum(item.price * item.quantity for item in order.items)
    order_dict = order.model_dump()

    # Always store username for ownership
    order_dict["user_id"] = current_user.username
    order_dict["vendor_id"] = vendor_id
    order_dict["total_amount"] = total

    result = await orders_collection.insert_one(order_dict)
    new_order = await orders_collection.find_one({"_id": result.inserted_id})
    return serialize_order(new_order)


# ---------- GET ORDERS ----------
@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    current_user: Annotated[User, Depends(get_current_active_user)],
    search: str | None = None,
):
    if current_user.role == "admin":
        query = {}
    else:
        query = {"user_id": current_user.username}

    orders = await orders_collection.find(query).to_list(length=None)

    if search:
        search_lower = search.lower()
        filtered = []
        for order in orders:
            vendor = await vendors_collection.find_one({"_id": ObjectId(order["vendor_id"])})
            vendor_name = vendor.get("name", "").lower() if vendor else ""
            if (
                search_lower in vendor_name
                or search_lower in order.get("user_id", "").lower()
                or search_lower in str(order["_id"]).lower()
            ):
                filtered.append(order)
        orders = filtered

    return [serialize_order(order) for order in orders]


# ---------- GET SINGLE ORDER ----------
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    oid = validate_object_id(order_id)
    order = await orders_collection.find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != "admin" and order.get("user_id") != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized")

    return serialize_order(order)


# ---------- UPDATE ORDER ----------
@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    updated: OrderUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    oid = validate_object_id(order_id)
    existing = await orders_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")

    # admin can update ANY order
    # customers only their own
    if current_user.role != "admin" and existing.get("user_id") != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_dict = {k: v for k, v in updated.model_dump(exclude_none=True).items()}

    # recompute total if items changed
    if "items" in update_dict:
        update_dict["total_amount"] = sum(
            float(item["price"]) * int(item["quantity"])
            for item in update_dict["items"]
        )
        # ONLY reset to pending if items changed
        update_dict["status"] = "pending"

    # ensure order_date is never lost
    update_dict["order_date"] = existing.get("order_date")

    await orders_collection.update_one({"_id": oid}, {"$set": update_dict})
    updated_order = await orders_collection.find_one({"_id": oid})
    return serialize_order(updated_order)


# ---------- DELETE ORDER ----------
@router.delete("/{order_id}")
async def delete_order(
    order_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    oid = validate_object_id(order_id)
    existing = await orders_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role != "admin" and existing.get("user_id") != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized")

    await orders_collection.delete_one({"_id": oid})
    return {"message": "Order deleted successfully"}
