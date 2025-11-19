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
