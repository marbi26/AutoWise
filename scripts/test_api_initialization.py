import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from backend.app.main import app
from backend.app.database import db_manager
from starlette.testclient import TestClient

def run_tests():
    print("Connecting to database...")
    asyncio.run(db_manager.connect())
    print("Database connected. Initializing TestClient...")

    with TestClient(app) as client:
        # 1. Health
        r = client.get("/api/health")
        print(f"1. Health check: {r.status_code} - {r.json()}")
        assert r.status_code == 200

        # 2. Vehicles Catalog
        r = client.get("/api/vehicles?limit=5")
        v_data = r.json()
        print(f"2. Vehicles Catalog: {r.status_code} - Found {v_data['total']} vehicles in catalog")
        assert r.status_code == 200
        assert v_data["total"] > 0

        # 3. Filters metadata
        r = client.get("/api/vehicles/meta/filters")
        filter_data = r.json()
        print(f"3. Filters Meta: {r.status_code} - Brands found: {len(filter_data['brands']['cars'])} cars, {len(filter_data['brands']['bikes'])} bikes")
        assert r.status_code == 200

        # 4. Recommendation Engine
        rec_req = {
            "category": "car",
            "min_budget": 800000,
            "max_budget": 1600000,
            "safety_priority": "High",
            "primary_usage": "City",
            "top_k": 3
        }
        r = client.post("/api/recommendations", json=rec_req)
        rec_data = r.json()
        top_v = rec_data['recommendations'][0]['vehicle']
        print(f"4. Recommendations: {r.status_code} - Top Pick: {top_v['brand']} {top_v['model']} ({rec_data['recommendations'][0]['match_score']}%)")
        assert r.status_code == 200

        # 5. Car Price Prediction
        car_pred_req = {
            "brand": "Maruti Suzuki",
            "model": "Swift",
            "year": 2020,
            "km_driven": 42000,
            "fuel_type": "Petrol",
            "transmission": "Manual",
            "engine_cc": 1197.0
        }
        r = client.post("/api/prediction/car", json=car_pred_req)
        pred_data = r.json()
        print(f"5. Car Price Prediction: {r.status_code} - Predicted: ₹{pred_data['predicted_price']:,.0f} (Range: ₹{pred_data['price_range_low']:,.0f} - ₹{pred_data['price_range_high']:,.0f})")
        assert r.status_code == 200

        # 6. Bike Price Prediction
        bike_pred_req = {
            "brand": "Royal Enfield",
            "model": "Classic 350",
            "year": 2021,
            "km_driven": 22000,
            "engine_cc": 349.0
        }
        r = client.post("/api/prediction/bike", json=bike_pred_req)
        b_pred = r.json()
        print(f"6. Bike Price Prediction: {r.status_code} - Predicted: ₹{b_pred['predicted_price']:,.0f} (Range: ₹{b_pred['price_range_low']:,.0f} - ₹{b_pred['price_range_high']:,.0f})")
        assert r.status_code == 200

        # 7. Comparison
        v1 = v_data["items"][0]["vehicle_id"]
        v2 = v_data["items"][1]["vehicle_id"]
        r = client.post("/api/compare", json={"vehicle_ids": [v1, v2]})
        comp_data = r.json()
        print(f"7. Comparison: {r.status_code} - Parameters compared: {len(comp_data['comparison_table'])}")
        assert r.status_code == 200

        # 8. Ownership TCO Calculation
        tco_req = {
            "vehicle_id": v1,
            "ownership_years": 5,
            "annual_km": 12000,
            "fuel_price_per_litre": 102.5
        }
        r = client.post("/api/ownership/calculate", json=tco_req)
        tco_data = r.json()
        summary = tco_data['selected_period_summary']
        print(f"8. Ownership TCO: {r.status_code} - 5-Yr TCO: ₹{summary['total_cost_of_ownership']:,.0f} (₹{summary['cost_per_km']}/km)")
        assert r.status_code == 200

        # 9. Analytics Dashboard
        r = client.get("/api/analytics/dashboard")
        analytics_data = r.json()
        print(f"9. Analytics Dashboard: {r.status_code} - Total Vehicles in System: {analytics_data['overview']['total_vehicles']}")
        assert r.status_code == 200

        # 10. Auth Registration and Login
        test_user = {
            "username": "rohit_sharma_test",
            "email": "rohit_test@example.com",
            "password": "Password123!",
            "full_name": "Rohit Sharma"
        }
        r = client.post("/api/auth/register", json=test_user)
        print(f"10. Auth Register: {r.status_code}")
        assert r.status_code in [201, 400]

        r = client.post("/api/auth/login", json={"username": "rohit_sharma_test", "password": "Password123!"})
        print(f"11. Auth Login: {r.status_code}")
        assert r.status_code == 200
        token = r.json()["access_token"]

        # 12. Profile
        r = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {token}"})
        print(f"12. Auth Profile: {r.status_code} - Authenticated as: {r.json()['username']}")
        assert r.status_code == 200

        # 13. Bookmark / Saved Vehicles
        r = client.post(f"/api/saved-vehicles/{v1}", headers={"Authorization": f"Bearer {token}"})
        print(f"13. Save Vehicle: {r.status_code} - {r.json()['message']}")
        assert r.status_code == 200

        r = client.get("/api/saved-vehicles", headers={"Authorization": f"Bearer {token}"})
        print(f"14. Get Saved Vehicles: {r.status_code} - Count: {r.json()['count']}")
        assert r.status_code == 200
        assert r.json()["count"] >= 1

    print("\n✓ ALL 14 API MODULES FULLY TESTED & VERIFIED!")

if __name__ == "__main__":
    run_tests()
