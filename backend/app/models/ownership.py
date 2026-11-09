from pydantic import BaseModel, Field
from typing import Optional, List

class OwnershipCalculateRequest(BaseModel):
    vehicle_id: str
    purchase_price: Optional[float] = None
    ownership_years: int = Field(5, ge=1, le=10, description="1, 3, or 5 years")
    annual_km: float = Field(12000.0, ge=1000, le=100000, description="Estimated km per year")
    fuel_price_per_litre: float = Field(100.0, ge=40, le=200, description="Current fuel cost in INR/L")
    down_payment_percentage: float = Field(20.0, ge=0, le=100)
    loan_interest_rate: float = Field(9.5, ge=0, le=25)
    loan_tenure_years: int = Field(5, ge=1, le=7)

class CostBreakdown(BaseModel):
    fuel_expense: float
    maintenance_and_servicing: float
    insurance_expense: float
    registration_and_taxes: float
    loan_interest_paid: float
    depreciation_loss: float
    estimated_resale_value: float
    total_cost_of_ownership: float
    cost_per_km: float

class OwnershipCalculateResponse(BaseModel):
    vehicle: dict
    ownership_years: int
    annual_km: float
    breakdown_by_year: dict  # year -> CostBreakdown
    selected_period_summary: CostBreakdown
    formula_explanation: str
    assumptions: dict
