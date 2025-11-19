from datetime import datetime, UTC

from pydantic import BaseModel, EmailStr, Field


class Vendor(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
