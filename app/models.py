from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional
from datetime import datetime, UTC


# Vendor model
class Vendor(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# Order Item model
class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float


# Order model
class Order(BaseModel):
    vendor_id: str
    order_date: datetime = Field(default_factory=lambda: datetime.now(UTC))

    items: List[OrderItem]
    status: str

    # total is optional because we'll calculate it in main.py
    total_amount: float | None = None


# Order Model for creating/updating order
class OrderCreate(BaseModel):
    vendor_id: str
    order_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    items: List[OrderItem]
    status: str
    special_instructions: Optional[str] = None
    due_at: Optional[datetime] = None


# Order Model for storing/returning
class OrderResponse(BaseModel):
    id: str
    vendor_id: str
    order_date: str
    items: List[OrderItem]
    status: str
    total_amount: float
    special_instructions: Optional[str] = None
    due_at: Optional[str] = None


# Products model
class Product(BaseModel):
    id: int
    title: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[HttpUrl] = None
    rating: Optional[dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
