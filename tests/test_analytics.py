import pytest

def test_analytics_dashboard_metrics(client):
    response = client.get("/api/analytics/dashboard")
    assert response.status_code == 200
    data = response.json()

    assert "overview" in data
    assert data["overview"]["total_vehicles"] >= 50
    assert data["overview"]["total_cars"] > 0
    assert data["overview"]["total_bikes"] > 0
    assert data["overview"]["total_vehicles"] == data["overview"]["total_cars"] + data["overview"]["total_bikes"]

    assert "charts" in data
    assert "popular_brands" in data["charts"]
    assert len(data["charts"]["popular_brands"]) > 0

    assert "averages" in data
    assert data["averages"]["avg_car_price_inr"] > 0
    assert data["averages"]["avg_bike_price_inr"] > 0
