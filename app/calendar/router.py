from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from bson import ObjectId
from app.database import orders_collection
from app.orders.service import serialize_order

router = APIRouter(prefix="/calendar", tags=["Calendar"])

# ---------- Helpers ----------
def validate_object_id(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    return ObjectId(id)


# ---------- Routes ----------
@router.get("/")
async def get_orders_in_range(
    start: datetime = Query(..., description="Start date (inclusive)"),
    end: datetime = Query(..., description="End date (inclusive)"),
):
    """Return all orders with due dates within a given range."""
    query = {"due_at": {"$gte": start, "$lte": end}}
    orders = []
    async for order in orders_collection.find(query):
        orders.append(serialize_order(order))
    return orders


@router.put("/{order_id}")
async def update_order_due_date(order_id: str, new_due_at: datetime):
    """Update an order's due date (used by calendar drag-and-drop)."""
    oid = validate_object_id(order_id)

    result = await orders_collection.update_one(
        {"_id": oid}, {"$set": {"due_at": new_due_at}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    updated_order = await orders_collection.find_one({"_id": oid})
    return serialize_order(updated_order)
