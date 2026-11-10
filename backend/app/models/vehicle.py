from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class VehicleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    vehicle_id: str
    category: str
    brand: str
    model: str
    variant: Optional[str] = ""
    year: int
    price_ex_showroom: float
    on_road_price_est: float
    fuel_type: str
    transmission: str
    mileage_kmpl: float
    engine_cc: float
    power_bhp: float
    torque_nm: float
    safety_rating: Optional[float] = 3.0
    seating_capacity: Optional[int] = 5
    boot_space_l: Optional[float] = 0.0
    body_type: Optional[str] = "Hatchback"
    usage_suitability: Optional[str] = "Mixed"
    features: Optional[List[str]] = []
    image_url: Optional[str] = ""
    condition: Optional[str] = "New"

class VehicleListResponse(BaseModel):
    items: List[VehicleResponse]
    total: int
    page: int
    total_pages: int
    filters_applied: dict
