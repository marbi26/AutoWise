from pydantic import BaseModel, Field
from typing import List, Optional

class CarPredictionRequest(BaseModel):
    brand: str = Field(..., example="Maruti Suzuki")
    model: str = Field(..., example="Swift")
    year: int = Field(..., ge=2000, le=2026, example=2020)
    km_driven: float = Field(..., ge=100, le=500000, example=45000)
    fuel_type: str = Field(..., example="Petrol")
    transmission: str = Field(..., example="Manual")
    engine_cc: Optional[float] = Field(1197.0, example=1197.0)
    mileage_kmpl: Optional[float] = Field(22.0, example=22.0)
    seller_type: Optional[str] = Field("Individual", example="Individual")
    owner: Optional[str] = Field("First Owner", example="First Owner")
    seats: Optional[int] = Field(5, example=5)

class BikePredictionRequest(BaseModel):
    brand: str = Field(..., example="Royal Enfield")
    model: str = Field(..., example="Classic 350")
    year: int = Field(..., ge=2005, le=2026, example=2021)
    km_driven: float = Field(..., ge=100, le=300000, example=22000)
    engine_cc: Optional[float] = Field(349.0, example=349.0)
    mileage_kmpl: Optional[float] = Field(36.0, example=36.0)
    seller_type: Optional[str] = Field("Individual", example="Individual")
    owner: Optional[str] = Field("First Owner", example="First Owner")

class FeatureImpact(BaseModel):
    feature: str
    importance_percentage: float

class PredictionResponse(BaseModel):
    category: str
    predicted_price: float
    price_range_low: float
    price_range_high: float
    confidence_interval_percentage: float = 95.0
    model_name: str
    model_r2_score: float
    model_mae_inr: float
    feature_importances: List[FeatureImpact]
    disclaimer: str
