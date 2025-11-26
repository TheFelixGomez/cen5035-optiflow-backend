from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone

from app.database import vendors_collection
from datetime import datetime, timezone

from app.database import vendors_collection
from app.vendors.models import Vendor

router = APIRouter(prefix="/vendors", tags=["Vendors"])


# ---------- Helper ----------
# ---------- Helper ----------
def vendor_serializer(vendor) -> dict:
    return {
        "id": str(vendor["_id"]),
        "name": vendor["name"],
        "email": vendor["email"],
        "phone": vendor["phone"],
        "address": vendor["address"],
        "created_at": str(vendor.get("created_at")),
    }


# ---------- CRUD Routes ----------
@router.post("/", response_model=dict)
# ---------- CRUD Routes ----------
@router.post("/", response_model=dict)
async def create_vendor(vendor: Vendor):
    vendor_dict = vendor.model_dump()
    vendor_dict["created_at"] = datetime.now(timezone.utc)
    result = await vendors_collection.insert_one(vendor_dict)
    new_vendor = await vendors_collection.find_one({"_id": result.inserted_id})
    return vendor_serializer(new_vendor)
    vendor_dict["created_at"] = datetime.now(timezone.utc)
    result = await vendors_collection.insert_one(vendor_dict)
    new_vendor = await vendors_collection.find_one({"_id": result.inserted_id})
    return vendor_serializer(new_vendor)


@router.get("/", response_model=list[dict])
@router.get("/", response_model=list[dict])
async def get_vendors():
    vendors = []
    async for vendor in vendors_collection.find():
        vendors.append(vendor_serializer(vendor))
    async for vendor in vendors_collection.find():
        vendors.append(vendor_serializer(vendor))
    return vendors


@router.get("/{vendor_id}", response_model=dict)
@router.get("/{vendor_id}", response_model=dict)
async def get_vendor(vendor_id: str):
    if not ObjectId.is_valid(vendor_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    vendor = await vendors_collection.find_one({"_id": ObjectId(vendor_id)})
    if not ObjectId.is_valid(vendor_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    vendor = await vendors_collection.find_one({"_id": ObjectId(vendor_id)})
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor_serializer(vendor)
    return vendor_serializer(vendor)


@router.put("/{vendor_id}", response_model=dict)
@router.put("/{vendor_id}", response_model=dict)
async def update_vendor(vendor_id: str, updated: Vendor):
    if not ObjectId.is_valid(vendor_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    update_data = {k: v for k, v in updated.model_dump().items() if v is not None}
    result = await vendors_collection.update_one(
        {"_id": ObjectId(vendor_id)}, {"$set": update_data}
    if not ObjectId.is_valid(vendor_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    update_data = {k: v for k, v in updated.model_dump().items() if v is not None}
    result = await vendors_collection.update_one(
        {"_id": ObjectId(vendor_id)}, {"$set": update_data}
    )
    if result.matched_count == 0:
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    updated_vendor = await vendors_collection.find_one({"_id": ObjectId(vendor_id)})
    return vendor_serializer(updated_vendor)
    updated_vendor = await vendors_collection.find_one({"_id": ObjectId(vendor_id)})
    return vendor_serializer(updated_vendor)


@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: str):
    if not ObjectId.is_valid(vendor_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = await vendors_collection.delete_one({"_id": ObjectId(vendor_id)})
    if not ObjectId.is_valid(vendor_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = await vendors_collection.delete_one({"_id": ObjectId(vendor_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}

