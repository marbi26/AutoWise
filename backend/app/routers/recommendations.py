from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import Optional

from backend.app.database import db_manager
from backend.app.models.recommendation import RecommendationRequest, RecommendationResponse, FeedbackRequest
from backend.app.services.recommendation_service import recommendation_service
from backend.app.auth.jwt_handler import get_optional_current_user, get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.post("", response_model=RecommendationResponse)
async def generate_recommendations(
    req: RecommendationRequest,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    user_id = str(current_user["_id"]) if current_user else None
    
    # Execute recommendation engine
    pref_dict = req.model_dump()
    result = recommendation_service.recommend(pref_dict, user_id=user_id, top_k=req.top_k)

    # If logged in, save to history
    if user_id:
        history_doc = {
            "user_id": user_id,
            "category": req.category,
            "query_parameters": pref_dict,
            "results": [
                {
                    "vehicle_id": r["vehicle"]["vehicle_id"],
                    "match_score": r["match_score"],
                    "matching_features": r["matching_features"],
                    "reasons": r["reasons"]
                }
                for r in result["recommendations"]
            ],
            "methodology": result["methodology"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db_manager.get_collection("recommendations").insert_one(history_doc)

    return RecommendationResponse(
        category=result["category"],
        total_evaluated=result["total_evaluated"],
        recommendations=result["recommendations"],
        alternatives=result["alternatives"],
        methodology=result["methodology"],
        applied_filters=result["applied_filters"]
    )

@router.get("/history")
async def get_recommendation_history(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    rec_col = db_manager.get_collection("recommendations")
    cursor = rec_col.find({"user_id": user_id}).sort("created_at", -1).limit(15)
    items = await cursor.to_list()
    return {"user_id": user_id, "count": len(items), "history": items}

@router.post("/feedback")
async def submit_feedback(
    fb: FeedbackRequest,
    current_user: Optional[dict] = Depends(get_optional_current_user)
):
    user_id = str(current_user["_id"]) if current_user else "anonymous_guest"
    interaction_doc = {
        "user_id": user_id,
        "vehicle_id": fb.vehicle_id,
        "interaction_type": fb.feedback_type,
        "rating": fb.rating or (5 if fb.feedback_type == "like" else 1),
        "metadata": {"recommendation_id": fb.recommendation_id},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db_manager.get_collection("user_interactions").insert_one(interaction_doc)
    return {"status": "success", "message": "Feedback recorded successfully."}

@router.get("/similar/{vehicle_id}")
async def get_similar_vehicles(vehicle_id: str, k: int = 4):
    similar = recommendation_service.get_similar_vehicles(vehicle_id, top_k=k)
    return {"vehicle_id": vehicle_id, "similar_vehicles": similar}
