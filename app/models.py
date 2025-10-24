from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List
from typing import Optional
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
    order_date: datetime = Field(default_factory=lambda: datetime.now(UTC))

    items: List[OrderItem]
    status: str

    # total is optional because we'll calculate it in main.py TODO: move this into anoter model
    total_amount: float | None = None


# Products model

class Product(BaseModel):
    id: int                        # id del fakestoreapi
    title: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[HttpUrl] = None
    rating: Optional[dict] = None           # la API devuelve rating {rate, count}
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))