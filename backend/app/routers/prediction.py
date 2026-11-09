from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from typing import Optional

from backend.app.database import db_manager
from backend.app.models.prediction import CarPredictionRequest, BikePredictionRequest, PredictionResponse
from backend.app.services.prediction_service import prediction_service
from backend.app.auth.jwt_handler import get_optional_current_user

router = APIRouter(prefix="/api/prediction", tags=["Price Prediction"])

@router.post("/car", response_model=PredictionResponse)
async def predict_car_price(
    req: CarPredictionRequest,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    result = prediction_service.predict_car(req)

    # Save prediction history if user is logged in
    user_id = str(current_user["_id"]) if current_user else "guest"
    pred_doc = {
        "user_id": user_id,
        "category": "car",
        "inputs": req.model_dump(),
        "predicted_price": result.predicted_price,
        "price_range_low": result.price_range_low,
        "price_range_high": result.price_range_high,
        "model_name": result.model_name,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db_manager.get_collection("predictions").insert_one(pred_doc)

    return result

@router.post("/bike", response_model=PredictionResponse)
async def predict_bike_price(
    req: BikePredictionRequest,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    result = prediction_service.predict_bike(req)

    user_id = str(current_user["_id"]) if current_user else "guest"
    pred_doc = {
        "user_id": user_id,
        "category": "bike",
        "inputs": req.model_dump(),
        "predicted_price": result.predicted_price,
        "price_range_low": result.price_range_low,
        "price_range_high": result.price_range_high,
        "model_name": result.model_name,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db_manager.get_collection("predictions").insert_one(pred_doc)

    return result

@router.get("/models-meta")
async def get_models_metadata():
    return prediction_service.get_meta()
