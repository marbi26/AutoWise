from typing import Dict, Any
from backend.app.models.ownership import OwnershipCalculateRequest, OwnershipCalculateResponse, CostBreakdown

class OwnershipService:
    @staticmethod
    def calculate_tco(vehicle: Dict[str, Any], req: OwnershipCalculateRequest) -> OwnershipCalculateResponse:
        price = req.purchase_price if req.purchase_price and req.purchase_price > 0 else float(vehicle.get("on_road_price_est") or vehicle.get("price_ex_showroom", 500000))
        is_car = vehicle.get("category") == "car"
        mileage = max(5.0, float(vehicle.get("mileage_kmpl", 18.0)))
        
        annual_km = req.annual_km
        fuel_price = req.fuel_price_per_litre

        # Loan Calculation
        down_payment = price * (req.down_payment_percentage / 100.0)
        loan_amount = price - down_payment
        monthly_rate = (req.loan_interest_rate / 100.0) / 12.0
        tenure_months = req.loan_tenure_years * 12

        if loan_amount > 0 and monthly_rate > 0:
            emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
        else:
            emi = 0.0

        # Yearly modeling
        breakdowns = {}
        cumulative_fuel = 0.0
        cumulative_maint = 0.0
        cumulative_ins = 0.0
        cumulative_interest = 0.0

        current_loan_balance = loan_amount

        for yr in range(1, 6):
            # 1. Fuel cost this year
            annual_litres = annual_km / mileage
            yr_fuel = annual_litres * fuel_price * (1.0 + (yr - 1) * 0.03) # 3% annual fuel inflation
            cumulative_fuel += yr_fuel

            # 2. Maintenance cost
            if is_car:
                base_maint = 5000 if yr == 1 else (10000 if yr <= 3 else 18000)
            else:
                base_maint = 1500 if yr == 1 else (3000 if yr <= 3 else 5000)
            cumulative_maint += base_maint

            # 3. Insurance cost based on depreciated IDV
            idv_factor = (1.0 - 0.15) if yr == 1 else ((1.0 - 0.15) * ((1.0 - 0.10) ** (yr - 1)))
            yr_idv = price * idv_factor
            yr_ins = yr_idv * (0.028 if is_car else 0.022)
            cumulative_ins += yr_ins

            # 4. Loan Interest for 12 months
            yr_interest = 0.0
            if emi > 0 and yr <= req.loan_tenure_years:
                for _ in range(12):
                    month_interest = current_loan_balance * monthly_rate
                    principal_paid = emi - month_interest
                    yr_interest += month_interest
                    current_loan_balance = max(0.0, current_loan_balance - principal_paid)
            cumulative_interest += yr_interest

            # 5. Resale Value at end of year yr
            # Indian standard depreciation: Yr 1: -15%, Yr 2: -25%, Yr 3: -35%, Yr 4: -44%, Yr 5: -52%
            resale_factors = {1: 0.85, 2: 0.75, 3: 0.65, 4: 0.56, 5: 0.48}
            resale_val = price * resale_factors.get(yr, 0.40)
            depreciation_loss = price - resale_val

            # TCO Formula: Actual Cash Outflow + Lost Value =
            # Purchase Price + Loan Interest + Fuel + Maintenance + Insurance - Resale Value
            total_tco = (price + cumulative_interest + cumulative_fuel + cumulative_maint + cumulative_ins) - resale_val
            cost_per_km = total_tco / (annual_km * yr)

            breakdowns[str(yr)] = CostBreakdown(
                fuel_expense=round(cumulative_fuel, 0),
                maintenance_and_servicing=round(cumulative_maint, 0),
                insurance_expense=round(cumulative_ins, 0),
                registration_and_taxes=round(price * 0.12, 0),
                loan_interest_paid=round(cumulative_interest, 0),
                depreciation_loss=round(depreciation_loss, 0),
                estimated_resale_value=round(resale_val, 0),
                total_cost_of_ownership=round(total_tco, 0),
                cost_per_km=round(cost_per_km, 2)
            )

        selected_yr_str = str(req.ownership_years) if str(req.ownership_years) in breakdowns else "5"
        summary = breakdowns[selected_yr_str]

        return OwnershipCalculateResponse(
            vehicle=vehicle,
            ownership_years=req.ownership_years,
            annual_km=annual_km,
            breakdown_by_year=breakdowns,
            selected_period_summary=summary,
            formula_explanation="Total Cost of Ownership (TCO) = (On-Road Purchase Price + Total Fuel Expenses + Servicing & Maintenance + Insurance Premiums + Net Loan Interest) - Estimated Vehicle Resale Value",
            assumptions={
                "annual_fuel_inflation_rate": "3.0%",
                "fuel_price_base": f"₹{fuel_price}/L",
                "depreciation_model": "Indian Automotive ARAI/IRDAI standard declining balance (15% Yr 1, then ~8-10% annually)",
                "disclaimer": "Calculated figures represent mathematical projections based on historical Indian automotive averages. Driving behavior, regional fuel taxes, periodic repairs, and individual vehicle upkeep may alter actual lifetime ownership costs."
            }
        )

ownership_service = OwnershipService()
