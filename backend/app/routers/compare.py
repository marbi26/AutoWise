from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone

from backend.app.database import db_manager
from backend.app.models.comparison import CompareRequest, CompareResponse
from backend.app.services.comparison_service import comparison_service
from backend.app.auth.jwt_handler import get_optional_current_user

router = APIRouter(prefix="/api/compare", tags=["Vehicle Comparison"])

@router.post("", response_model=CompareResponse)
async def compare_vehicles(
    req: CompareRequest,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    unique_ids = list(dict.fromkeys(req.vehicle_ids))
    if len(unique_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least two distinct vehicle IDs to compare."
        )

    vehicles_col = db_manager.get_collection("vehicles")
    vehicles = []
    for vid in unique_ids:
        v = await vehicles_col.find_one({"vehicle_id": vid})
        if v:
            vehicles.append(v)

    if len(vehicles) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"At least two valid vehicles must be found to compare. Found: {len(vehicles)}"
        )

    # Save to comparisons history if user logged in
    if current_user:
        user_id = str(current_user["_id"])
        comp_doc = {
            "user_id": user_id,
            "vehicle_ids": req.vehicle_ids,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db_manager.get_collection("comparisons").insert_one(comp_doc)

    return comparison_service.compare_vehicles(vehicles)
