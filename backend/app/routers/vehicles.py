import math
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from backend.app.database import db_manager
from backend.app.models.vehicle import VehicleResponse, VehicleListResponse
from backend.app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])

@router.get("", response_model=VehicleListResponse)
async def list_vehicles(
    category: Optional[str] = Query(None, description="'car' or 'bike'"),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    fuel_type: Optional[str] = Query(None),
    transmission: Optional[str] = Query(None),
    body_type: Optional[str] = Query(None),
    safety_rating: Optional[float] = Query(None),
    sort_by: Optional[str] = Query("price_asc", description="price_asc, price_desc, mileage_desc, safety_desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50)
):
    query = {}
    if category:
        query["category"] = category.lower()
    if brand:
        query["brand"] = brand
    if fuel_type:
        query["fuel_type"] = fuel_type
    if transmission:
        query["transmission"] = transmission
    if body_type:
        query["body_type"] = body_type

    # Price range
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        query["price_ex_showroom"] = price_filter

    if safety_rating is not None:
        query["safety_rating"] = {"$gte": safety_rating}

    vehicles_col = db_manager.get_collection("vehicles")
    cursor = vehicles_col.find(query)

    # Sorting
    if sort_by == "price_asc":
        cursor = cursor.sort("price_ex_showroom", 1)
    elif sort_by == "price_desc":
        cursor = cursor.sort("price_ex_showroom", -1)
    elif sort_by == "mileage_desc":
        cursor = cursor.sort("mileage_kmpl", -1)
    elif sort_by == "safety_desc":
        cursor = cursor.sort("safety_rating", -1)

    all_matched = await cursor.to_list()
    total = len(all_matched)
    total_pages = max(1, math.ceil(total / limit))

    start_idx = (page - 1) * limit
    paged_items = all_matched[start_idx : start_idx + limit]

    return VehicleListResponse(
        items=paged_items,
        total=total,
        page=page,
        total_pages=total_pages,
        filters_applied={
            "category": category, "brand": brand, "min_price": min_price,
            "max_price": max_price, "fuel_type": fuel_type, "transmission": transmission,
            "body_type": body_type, "sort_by": sort_by
        }
    )

@router.get("/meta/filters")
async def get_filter_meta():
    vehicles_col = db_manager.get_collection("vehicles")
    cars_brands = await vehicles_col.distinct("brand", {"category": "car"})
    bikes_brands = await vehicles_col.distinct("brand", {"category": "bike"})
    fuel_types = await vehicles_col.distinct("fuel_type")
    transmissions = await vehicles_col.distinct("transmission")
    body_types = await vehicles_col.distinct("body_type")

    return {
        "brands": {
            "cars": sorted(cars_brands),
            "bikes": sorted(bikes_brands)
        },
        "fuel_types": sorted(fuel_types),
        "transmissions": sorted(transmissions),
        "body_types": sorted(body_types),
        "budget_ranges": {
            "cars": [
                {"label": "Under ₹8 Lakh", "min": 0, "max": 800000},
                {"label": "₹8 Lakh - ₹15 Lakh", "min": 800000, "max": 1500000},
                {"label": "₹15 Lakh - ₹25 Lakh", "min": 1500000, "max": 2500000},
                {"label": "Above ₹25 Lakh", "min": 2500000, "max": 10000000}
            ],
            "bikes": [
                {"label": "Under ₹1 Lakh", "min": 0, "max": 100000},
                {"label": "₹1 Lakh - ₹2 Lakh", "min": 100000, "max": 200000},
                {"label": "₹2 Lakh - ₹3.5 Lakh", "min": 200000, "max": 350000},
                {"label": "Above ₹3.5 Lakh", "min": 350000, "max": 1500000}
            ]
        }
    }

@router.get("/search")
async def search_vehicles(q: str = Query(..., min_length=1)):
    q_lower = q.lower()
    vehicles_col = db_manager.get_collection("vehicles")
    all_vehicles = await vehicles_col.find({}).to_list()

    results = []
    for v in all_vehicles:
        brand = v.get("brand", "").lower()
        model = v.get("model", "").lower()
        variant = v.get("variant", "").lower()
        body = v.get("body_type", "").lower()

        if q_lower in f"{brand} {model} {variant} {body}":
            results.append(v)
            if len(results) >= 20:
                break

    return {"query": q, "count": len(results), "items": results}

@router.get("/{vehicle_id}")
async def get_vehicle_detail(vehicle_id: str):
    vehicles_col = db_manager.get_collection("vehicles")
    vehicle = await vehicles_col.find_one({"vehicle_id": vehicle_id})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Get similar vehicles
    similar = recommendation_service.get_similar_vehicles(vehicle_id, top_k=4)

    return {
        "vehicle": vehicle,
        "similar_vehicles": similar
    }
