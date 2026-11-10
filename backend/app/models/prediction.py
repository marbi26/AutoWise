from pydantic import BaseModel, Field
from typing import List, Optional

class CarPredictionRequest(BaseModel):
    brand: str = Field(..., examples=["Maruti Suzuki"])
    model: str = Field(..., examples=["Swift"])
    year: int = Field(..., ge=2000, le=2026, examples=[2020])
    km_driven: float = Field(..., ge=100, le=500000, examples=[45000])
    fuel_type: str = Field(..., examples=["Petrol"])
    transmission: str = Field(..., examples=["Manual"])
    engine_cc: Optional[float] = Field(1197.0, examples=[1197.0])
    mileage_kmpl: Optional[float] = Field(22.0, examples=[22.0])
    seller_type: Optional[str] = Field("Individual", examples=["Individual"])
    owner: Optional[str] = Field("First Owner", examples=["First Owner"])
    seats: Optional[int] = Field(5, examples=[5])

class BikePredictionRequest(BaseModel):
    brand: str = Field(..., examples=["Royal Enfield"])
    model: str = Field(..., examples=["Classic 350"])
    year: int = Field(..., ge=2005, le=2026, examples=[2021])
    km_driven: float = Field(..., ge=100, le=300000, examples=[22000])
    engine_cc: Optional[float] = Field(349.0, examples=[349.0])
    mileage_kmpl: Optional[float] = Field(36.0, examples=[36.0])
    seller_type: Optional[str] = Field("Individual", examples=["Individual"])
    owner: Optional[str] = Field("First Owner", examples=["First Owner"])

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
