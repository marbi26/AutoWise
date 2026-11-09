from fastapi import APIRouter, HTTPException
from backend.app.database import db_manager
from backend.app.models.ownership import OwnershipCalculateRequest, OwnershipCalculateResponse
from backend.app.services.ownership_service import ownership_service

router = APIRouter(prefix="/api/ownership", tags=["Ownership Cost"])

@router.post("/calculate", response_model=OwnershipCalculateResponse)
async def calculate_ownership_cost(req: OwnershipCalculateRequest):
    vehicle = await db_manager.get_collection("vehicles").find_one({"vehicle_id": req.vehicle_id})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return ownership_service.calculate_tco(vehicle, req)
