import pytest

def test_ownership_cost_calculation_5_years(client):
    # Fetch a real vehicle ID
    v_res = client.get("/api/vehicles?category=car&limit=1")
    v_id = v_res.json()["items"][0]["vehicle_id"]

    payload = {
        "vehicle_id": v_id,
        "purchase_price": 1000000.0,
        "ownership_years": 5,
        "annual_km": 12000.0,
        "fuel_price_per_litre": 102.5,
        "down_payment_percentage": 20.0,
        "loan_interest_rate": 9.5,
        "loan_tenure_years": 5
    }
    response = client.post("/api/ownership/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "selected_period_summary" in data
    summary = data["selected_period_summary"]

    assert summary["fuel_expense"] > 0
    assert summary["maintenance_and_servicing"] > 0
    assert summary["insurance_expense"] > 0
    assert summary["estimated_resale_value"] > 0
    assert summary["total_cost_of_ownership"] > 0
    assert summary["cost_per_km"] > 0

    assert "breakdown_by_year" in data
    assert "5" in data["breakdown_by_year"]
    assert "formula_explanation" in data

def test_ownership_cost_tenures(client):
    v_res = client.get("/api/vehicles?category=bike&limit=1")
    v_id = v_res.json()["items"][0]["vehicle_id"]

    for years in [1, 3, 5]:
        payload = {
            "vehicle_id": v_id,
            "ownership_years": years,
            "annual_km": 8000.0,
            "fuel_price_per_litre": 102.5
        }
        res = client.post("/api/ownership/calculate", json=payload)
        assert res.status_code == 200
        assert res.json()["ownership_years"] == years
