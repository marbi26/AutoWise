from typing import List, Dict, Any
from backend.app.models.comparison import CompareResponse, SpecificationItem, RadarScore

class ComparisonService:
    @staticmethod
    def compare_vehicles(vehicles: List[Dict[str, Any]]) -> CompareResponse:
        v_ids = [v["vehicle_id"] for v in vehicles]
        
        # 1. Structured parameter specifications
        params = [
            {"key": "price_ex_showroom", "label": "Ex-Showroom Price", "unit": "₹", "higher_is_better": False, "format": lambda x: f"₹{x:,.0f}"},
            {"key": "on_road_price_est", "label": "Est. On-Road Price", "unit": "₹", "higher_is_better": False, "format": lambda x: f"₹{x:,.0f}"},
            {"key": "mileage_kmpl", "label": "ARAI Mileage", "unit": "kmpl", "higher_is_better": True, "format": lambda x: f"{x} kmpl"},
            {"key": "engine_cc", "label": "Engine Displacement", "unit": "cc", "higher_is_better": True, "format": lambda x: f"{x} cc"},
            {"key": "power_bhp", "label": "Maximum Power", "unit": "bhp", "higher_is_better": True, "format": lambda x: f"{x} bhp"},
            {"key": "torque_nm", "label": "Peak Torque", "unit": "Nm", "higher_is_better": True, "format": lambda x: f"{x} Nm"},
            {"key": "safety_rating", "label": "NCAP Safety Rating", "unit": "Stars", "higher_is_better": True, "format": lambda x: f"{int(x)} ★"},
            {"key": "fuel_type", "label": "Fuel Type", "unit": "", "higher_is_better": None, "format": lambda x: str(x)},
            {"key": "transmission", "label": "Transmission", "unit": "", "higher_is_better": None, "format": lambda x: str(x)},
            {"key": "seating_capacity", "label": "Seating Capacity", "unit": "Persons", "higher_is_better": True, "format": lambda x: f"{x} Seats"},
            {"key": "boot_space_l", "label": "Boot Space", "unit": "Litres", "higher_is_better": True, "format": lambda x: f"{x} L" if x > 0 else "N/A"},
            {"key": "est_annual_maint", "label": "Est. Annual Maintenance", "unit": "₹", "higher_is_better": False, "format": lambda x: f"₹{x:,.0f}"}
        ]

        table_items = []
        for p in params:
            values_dict = {}
            for v in vehicles:
                val = v.get(p["key"])
                if p["key"] == "est_annual_maint":
                    # Estimate maintenance based on category & price: ~1.2% of car price or ₹3500 for bike
                    if v.get("category") == "car":
                        val = int(v.get("price_ex_showroom", 1000000) * 0.012)
                    else:
                        val = int(max(3000, v.get("price_ex_showroom", 150000) * 0.025))
                
                if val is None or val == "":
                    values_dict[v["vehicle_id"]] = "Not Specified"
                else:
                    values_dict[v["vehicle_id"]] = p["format"](val)

            # Determine winner for numeric columns
            winner_id = None
            if p["higher_is_better"] is not None:
                numeric_vals = {}
                for v in vehicles:
                    raw_val = v.get(p["key"])
                    if p["key"] == "est_annual_maint":
                        raw_val = int(v.get("price_ex_showroom", 1000000) * 0.012) if v.get("category") == "car" else int(max(3000, v.get("price_ex_showroom", 150000) * 0.025))
                    if isinstance(raw_val, (int, float)):
                        numeric_vals[v["vehicle_id"]] = raw_val

                if numeric_vals:
                    if p["higher_is_better"]:
                        winner_id = max(numeric_vals, key=numeric_vals.get)
                    else:
                        winner_id = min(numeric_vals, key=numeric_vals.get)

            table_items.append(SpecificationItem(
                parameter=p["label"],
                unit=p["unit"],
                values=values_dict,
                winner=winner_id
            ))

        # 2. Radar Chart Normalization across 5 Key Pillars
        radar_list = []
        for v in vehicles:
            is_car = v.get("category") == "car"
            # Performance score (power + torque)
            max_power = 200.0 if is_car else 50.0
            p_score = min(100.0, ((v.get("power_bhp", 80) / max_power) * 100.0))

            # Fuel economy
            max_mileage = 30.0 if is_car else 75.0
            fe_score = min(100.0, ((v.get("mileage_kmpl", 15) / max_mileage) * 100.0))

            # Safety score
            s_score = (v.get("safety_rating", 3) / 5.0) * 100.0

            # Space & Utility (boot + seating)
            if is_car:
                space_score = min(100.0, ((v.get("boot_space_l", 300) / 550.0) * 70.0 + (v.get("seating_capacity", 5) / 7.0) * 30.0))
            else:
                space_score = 60.0 if v.get("boot_space_l", 0) > 15 else 40.0

            # Value for Money (Features & Power per Lakh)
            lakhs = max(0.5, v.get("price_ex_showroom", 1000000) / 100000.0)
            vfm_score = max(30.0, min(95.0, 100.0 - (lakhs * (2.2 if is_car else 15.0))))

            radar_list.append(RadarScore(
                vehicle_id=v["vehicle_id"],
                vehicle_name=f"{v['brand']} {v['model']}",
                scores={
                    "Performance": round(p_score, 1),
                    "Fuel Economy": round(fe_score, 1),
                    "Safety": round(s_score, 1),
                    "Space & Utility": round(space_score, 1),
                    "Value for Money": round(vfm_score, 1)
                }
            ))

        # 3. Summary Verdict
        verdict_parts = []
        for v in vehicles:
            name = f"{v['brand']} {v['model']}"
            strengths = []
            if v.get("safety_rating", 0) >= 4:
                strengths.append("outstanding safety credentials")
            if v.get("mileage_kmpl", 0) >= (20 if v.get("category") == "car" else 50):
                strengths.append("exceptional fuel efficiency")
            if v.get("power_bhp", 0) >= (115 if v.get("category") == "car" else 24):
                strengths.append("commanding powertrain performance")
            if not strengths:
                strengths.append("balanced practicality for urban commuting")
            verdict_parts.append(f"**{name}** excels in {', '.join(strengths)}.")

        return CompareResponse(
            vehicles=vehicles,
            comparison_table=table_items,
            radar_scores=radar_list,
            summary_verdict=" ".join(verdict_parts)
        )

comparison_service = ComparisonService()
