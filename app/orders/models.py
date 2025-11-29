from datetime import UTC, datetime
from typing import List

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float


# Order Model for creating/updating order
class OrderCreate(BaseModel):
    vendor_id: str
    order_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    items: List[OrderItem]
    status: str
    special_instructions: str | None = None
    due_at: datetime | None = None


# Order Model for partial updates
class OrderUpdate(BaseModel):
    items: List[OrderItem] | None = None
    status: str | None = None
    special_instructions: str | None = None
    due_at: str | None = None
    vendor_id: str | None = None



# Order Model for storing/returning
class OrderResponse(BaseModel):
    id: str
    vendor_id: str
    user_id: str
    order_date: str
    items: List[OrderItem]
    status: str
    total_amount: float
    special_instructions: str | None = None
    due_at: datetime | None = None
