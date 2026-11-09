from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel

from backend.app.database import db_manager
from backend.app.auth.jwt_handler import get_current_user, get_optional_current_user

router = APIRouter(tags=["User Interactions & Bookmarks"])

class LogInteractionRequest(BaseModel):
    vehicle_id: str
    interaction_type: str  # view, click, search, compare

@router.get("/api/saved-vehicles")
async def get_saved_vehicles(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    saved_col = db_manager.get_collection("saved_vehicles")
    vehicles_col = db_manager.get_collection("vehicles")

    saved_records = await saved_col.find({"user_id": user_id}).sort("saved_at", -1).to_list()
    v_ids = [r["vehicle_id"] for r in saved_records]

    # Fetch vehicles
    matched_vehicles = []
    for vid in v_ids:
        v = await vehicles_col.find_one({"vehicle_id": vid})
        if v:
            matched_vehicles.append(v)

    return {
        "user_id": user_id,
        "count": len(matched_vehicles),
        "items": matched_vehicles
    }

@router.post("/api/saved-vehicles/{vehicle_id}")
async def save_vehicle(vehicle_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    saved_col = db_manager.get_collection("saved_vehicles")

    existing = await saved_col.find_one({"user_id": user_id, "vehicle_id": vehicle_id})
    if existing:
        return {"status": "exists", "message": "Vehicle already in your saved list."}

    doc = {
        "user_id": user_id,
        "vehicle_id": vehicle_id,
        "saved_at": datetime.now(timezone.utc).isoformat()
    }
    await saved_col.insert_one(doc)

    # Log interaction
    await db_manager.get_collection("user_interactions").insert_one({
        "user_id": user_id,
        "vehicle_id": vehicle_id,
        "interaction_type": "save",
        "rating": 5,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {"status": "saved", "message": "Vehicle saved to your profile."}

@router.delete("/api/saved-vehicles/{vehicle_id}")
async def remove_saved_vehicle(vehicle_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    saved_col = db_manager.get_collection("saved_vehicles")
    deleted = await saved_col.delete_one({"user_id": user_id, "vehicle_id": vehicle_id})
    return {"status": "removed" if deleted else "not_found"}

@router.post("/api/interactions")
async def log_interaction(
    req: LogInteractionRequest,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    user_id = str(current_user["_id"]) if current_user else "anonymous"
    doc = {
        "user_id": user_id,
        "vehicle_id": req.vehicle_id,
        "interaction_type": req.interaction_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db_manager.get_collection("user_interactions").insert_one(doc)
    return {"status": "logged"}
