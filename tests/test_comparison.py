import pytest

def test_vehicle_comparison_two_vehicles(client):
    # Fetch 2 real vehicles
    cat_res = client.get("/api/vehicles?category=car&limit=2")
    cars = cat_res.json()["items"]
    assert len(cars) >= 2
    car_ids = [cars[0]["vehicle_id"], cars[1]["vehicle_id"]]

    response = client.post("/api/compare", json={"vehicle_ids": car_ids})
    assert response.status_code == 200
    data = response.json()

    assert "vehicles" in data
    assert len(data["vehicles"]) == 2
    assert "comparison_table" in data
    assert len(data["comparison_table"]) > 0
    assert "radar_scores" in data
    assert len(data["radar_scores"]) == 2
    assert "summary_verdict" in data

def test_vehicle_comparison_validation_errors(client):
    # Fewer than 2 vehicles
    bad_req = client.post("/api/compare", json={"vehicle_ids": ["single_id"]})
    assert bad_req.status_code in [400, 422]

    # Non-existent vehicle IDs
    missing_req = client.post("/api/compare", json={"vehicle_ids": ["invalid_1", "invalid_2"]})
    assert missing_req.status_code in [400, 404]
