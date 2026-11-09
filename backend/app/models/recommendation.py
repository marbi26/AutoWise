from pydantic import BaseModel, Field
from typing import List, Optional, Any

class RecommendationRequest(BaseModel):
    category: str = Field("car", description="'car' or 'bike'")
    min_budget: Optional[float] = Field(0.0, description="Minimum budget in INR")
    max_budget: Optional[float] = Field(5000000.0, description="Maximum budget in INR")
    preferred_brands: Optional[List[str]] = Field([], description="List of preferred brands")
    fuel_types: Optional[List[str]] = Field([], description="Petrol, Diesel, Electric, CNG")
    transmissions: Optional[List[str]] = Field([], description="Manual, Automatic, AMT, CVT, DCT")
    min_mileage: Optional[float] = Field(0.0, description="Min mileage in kmpl")
    min_engine_cc: Optional[float] = Field(0.0, description="Min engine displacement")
    performance_priority: Optional[str] = Field("Medium", description="Low, Medium, High")
    safety_priority: Optional[str] = Field("Medium", description="Low, Medium, High")
    primary_usage: Optional[str] = Field("Mixed", description="City, Highway, Mixed")
    seating_capacity: Optional[int] = Field(None, description="Preferred seating capacity for cars")
    top_k: Optional[int] = Field(5, description="Number of recommendations to return")

class RecommendationItem(BaseModel):
    vehicle: dict
    match_score: float
    matching_features: List[str]
    reasons: str

class RecommendationResponse(BaseModel):
    category: str
    total_evaluated: int
    recommendations: List[RecommendationItem]
    alternatives: List[dict]
    methodology: str
    applied_filters: dict

class FeedbackRequest(BaseModel):
    recommendation_id: Optional[str] = None
    vehicle_id: str
    feedback_type: str = Field(..., description="'like', 'dislike', 'save', 'view'")
    rating: Optional[int] = Field(None, ge=1, le=5)
