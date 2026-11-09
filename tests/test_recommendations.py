import pytest

def test_car_recommendation_pipeline(client):
    req_body = {
        "category": "car",
        "min_budget": 700000,
        "max_budget": 1500000,
        "fuel_types": ["Petrol"],
        "safety_priority": "High",
        "primary_usage": "City",
        "top_k": 4
    }
    response = client.post("/api/recommendations", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    recs = data["recommendations"]
    assert len(recs) <= 4
    assert len(recs) > 0

    prev_score = 100.0
    for item in recs:
        score = item["match_score"]
        assert 0.0 <= score <= 100.0
        assert score <= prev_score + 0.01  # descending
        prev_score = score
        assert "vehicle" in item
        assert item["vehicle"]["category"] == "car"
        assert "reasons" in item
        assert isinstance(item["reasons"], str)
        assert len(item["reasons"]) > 0
        assert "matching_features" in item
        assert isinstance(item["matching_features"], list)

def test_bike_recommendation_pipeline(client):
    req_body = {
        "category": "bike",
        "min_budget": 80000,
        "max_budget": 250000,
        "primary_usage": "City",
        "top_k": 3
    }
    response = client.post("/api/recommendations", json=req_body)
    assert response.status_code == 200
    recs = response.json()["recommendations"]
    assert len(recs) > 0
    for item in recs:
        assert item["vehicle"]["category"] == "bike"
        assert item["match_score"] > 0

def test_recommendation_feedback(client):
    feedback_payload = {
        "vehicle_id": "car_tata_nexon",
        "feedback_type": "like",
        "rating": 5
    }
    res = client.post("/api/recommendations/feedback", json=feedback_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "message" in data
