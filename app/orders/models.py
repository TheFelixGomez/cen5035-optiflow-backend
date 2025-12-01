from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float

class OrderCreate(BaseModel):
    vendor_id: str
    order_date: datetime = Field(default_factory=datetime.utcnow)
    items: List[OrderItem]
    status: str
    special_instructions: Optional[str] = None
    due_at: Optional[datetime] = None

class OrderUpdate(BaseModel):
    items: Optional[List[OrderItem]] = None
    status: Optional[str] = None
    special_instructions: Optional[str] = None
    due_at: Optional[datetime] = None
    vendor_id: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    vendor_id: str
    user_id: str
    order_date: str
    items: List[OrderItem]
    status: str
    total_amount: float
    special_instructions: Optional[str] = None
    due_at: Optional[str] = None
