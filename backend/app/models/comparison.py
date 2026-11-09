from pydantic import BaseModel, Field
from typing import List, Optional

class CompareRequest(BaseModel):
    vehicle_ids: List[str] = Field(..., min_length=2, max_length=4, description="List of 2 to 4 vehicle IDs to compare")

class SpecificationItem(BaseModel):
    parameter: str
    unit: str
    values: dict  # vehicle_id -> value
    winner: Optional[str] = None

class RadarScore(BaseModel):
    vehicle_id: str
    vehicle_name: str
    scores: dict  # metric -> score (0-100)

class CompareResponse(BaseModel):
    vehicles: List[dict]
    comparison_table: List[SpecificationItem]
    radar_scores: List[RadarScore]
    summary_verdict: str
