import pytest

def test_get_vehicles_catalog(client):
    response = client.get("/api/vehicles?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert data["total"] > 0
    assert "items" in data
    assert len(data["items"]) <= 10

    # Validate structure of vehicle
    v = data["items"][0]
    assert "vehicle_id" in v
    assert "brand" in v
    assert "model" in v
    assert "price_ex_showroom" in v
    assert "category" in v

def test_filter_vehicles_by_category(client):
    car_res = client.get("/api/vehicles?category=car&limit=50")
    assert car_res.status_code == 200
    cars = car_res.json()["items"]
    assert len(cars) > 0
    assert all(c["category"] == "car" for c in cars)

    bike_res = client.get("/api/vehicles?category=bike&limit=50")
    assert bike_res.status_code == 200
    bikes = bike_res.json()["items"]
    assert len(bikes) > 0
    assert all(b["category"] == "bike" for b in bikes)

def test_filter_vehicles_by_price_and_brand(client):
    res = client.get("/api/vehicles?category=car&brand=Maruti Suzuki&min_price=500000&max_price=1200000")
    assert res.status_code == 200
    vehicles = res.json()["items"]
    for v in vehicles:
        assert v["brand"] == "Maruti Suzuki"
        assert 500000 <= v["price_ex_showroom"] <= 1200000

def test_search_vehicles(client):
    res = client.get("/api/vehicles/search?q=Nexon")
    assert res.status_code == 200
    results = res.json()["items"]
    assert len(results) > 0
    assert any("nexon" in v["model"].lower() for v in results)

def test_get_single_vehicle_and_not_found(client):
    # Fetch list first
    list_res = client.get("/api/vehicles?limit=1")
    first_v = list_res.json()["items"][0]
    v_id = first_v["vehicle_id"]

    # Fetch by valid ID
    single_res = client.get(f"/api/vehicles/{v_id}")
    assert single_res.status_code == 200
    assert single_res.json()["vehicle"]["vehicle_id"] == v_id
    assert single_res.json()["vehicle"]["model"] == first_v["model"]

    # Fetch by invalid ID
    not_found_res = client.get("/api/vehicles/non_existent_vehicle_99999")
    assert not_found_res.status_code == 404

def test_vehicles_meta_filters(client):
    res = client.get("/api/vehicles/meta/filters")
    assert res.status_code == 200
    meta = res.json()
    assert "brands" in meta
    assert "cars" in meta["brands"]
    assert "bikes" in meta["brands"]
    assert len(meta["brands"]["cars"]) > 0
    assert len(meta["brands"]["bikes"]) > 0
    assert "fuel_types" in meta
    assert "transmissions" in meta
