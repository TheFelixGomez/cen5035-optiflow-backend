from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.database import users_collection
from app.vendors.models import Vendor

router = APIRouter(prefix="/vendors", tags=["Vendors"])


def vendor_serializer(vendor) -> dict:
    return {
        "id": str(vendor["_id"]),
        "name": vendor["name"],
        "email": vendor["email"],
        "phone": vendor["phone"],
        "address": vendor["address"],
        "created_at": str(vendor["created_at"]),
    }


@router.post("/")
async def create_vendor(vendor: Vendor):
    vendor_dict = vendor.model_dump()
    result = await users_collection.insert_one(vendor_dict)
    vendor_dict["_id"] = str(result.inserted_id)
    return vendor_dict


@router.get("/")
async def get_vendors():
    vendors = []
    async for vendor in users_collection.find():
        vendor["_id"] = str(vendor["_id"])
        vendors.append(vendor)
    return vendors


@router.get("/{vendor_id}")
async def get_vendor(vendor_id: str):
    vendor = await users_collection.find_one({"_id": ObjectId(vendor_id)})
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    vendor["_id"] = str(vendor["_id"])
    return vendor


@router.put("/{vendor_id}")
async def update_vendor(vendor_id: str, updated: Vendor):
    result = await users_collection.update_one(
        {"_id": ObjectId(vendor_id)}, {"$set": updated.model_dump()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor updated successfully"}


@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: str):
    result = await users_collection.delete_one({"_id": ObjectId(vendor_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": "Vendor deleted successfully"}