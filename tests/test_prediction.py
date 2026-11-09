import pytest

def test_car_price_prediction_valid(client):
    payload = {
        "brand": "Maruti Suzuki",
        "model": "Swift",
        "year": 2019,
        "km_driven": 45000,
        "fuel_type": "Petrol",
        "transmission": "Manual",
        "engine_cc": 1197.0,
        "owner": "First Owner"
    }
    response = client.post("/api/prediction/car", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "predicted_price" in data
    assert data["predicted_price"] > 100000  # realistic resale price > 1 Lakh
    assert data["price_range_low"] <= data["predicted_price"]
    assert data["predicted_price"] <= data["price_range_high"]
    assert "feature_importances" in data
    assert len(data["feature_importances"]) > 0
    assert "model_name" in data

def test_bike_price_prediction_valid(client):
    payload = {
        "brand": "Royal Enfield",
        "model": "Classic 350",
        "year": 2021,
        "km_driven": 18000,
        "engine_cc": 349.0,
        "owner": "First Owner"
    }
    response = client.post("/api/prediction/bike", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "predicted_price" in data
    assert data["predicted_price"] > 40000  # realistic resale price
    assert data["price_range_low"] <= data["predicted_price"]
    assert data["predicted_price"] <= data["price_range_high"]
    assert "feature_importances" in data

def test_prediction_input_validation(client):
    bad_payload = {
        "brand": "Maruti Suzuki",
        "model": "Swift",
        "year": 2050,  # Unrealistic future year
        "km_driven": -5000,  # Negative km
        "fuel_type": "Petrol",
        "transmission": "Manual"
    }
    response = client.post("/api/prediction/car", json=bad_payload)
    assert response.status_code == 422  # Pydantic validation error
