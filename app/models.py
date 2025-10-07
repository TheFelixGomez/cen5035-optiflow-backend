from pydantic import BaseModel, Field, EmailStr
from typing import List
from datetime import datetime, UTC

# Vendor model
class Vendor(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    created_at: datetime = Field(default_factory=datetime.now(UTC))

# Order Item model
class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float

# Order model
class Order(BaseModel):
    vendor_id: str
    order_date: datetime = Field(default_factory=datetime.utcnow)
    items: List[OrderItem]
    status: str

    # total is optional because we'll calculate it in main.py
    total_amount: float | None = None
