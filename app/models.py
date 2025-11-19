from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


# Vendor model
class Vendor(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


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
