from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from bson import ObjectId
from app.database import orders_collection
from app.routers.orders_router import serialize_order

router = APIRouter(prefix="/calendar", tags=["Calendar"])


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
    """Update an order's due date (used by the calendar drag-and-drop)."""
    result = await orders_collection.update_one(
        {"_id": ObjectId(order_id)}, {"$set": {"due_at": new_due_at}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found or not updated")
    return {
        "message": "Order due date updated",
        "order_id": order_id,
        "due_at": new_due_at,
    }