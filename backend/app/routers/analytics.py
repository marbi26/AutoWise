from fastapi import APIRouter
from backend.app.database import db_manager

router = APIRouter(prefix="/api/analytics", tags=["Analytics Dashboard"])

@router.get("/dashboard")
async def get_dashboard_analytics():
    vehicles_col = db_manager.get_collection("vehicles")
    users_col = db_manager.get_collection("users")
    interactions_col = db_manager.get_collection("user_interactions")
    recs_col = db_manager.get_collection("recommendations")
    preds_col = db_manager.get_collection("predictions")

    all_vehicles = await vehicles_col.find({}).to_list()
    total_vehicles = len(all_vehicles)

    cars = [v for v in all_vehicles if v.get("category") == "car"]
    bikes = [v for v in all_vehicles if v.get("category") == "bike"]

    total_cars = len(cars)
    total_bikes = len(bikes)

    # 1. Category and Fuel distribution
    fuel_dist = {}
    for v in all_vehicles:
        f = v.get("fuel_type", "Petrol")
        fuel_dist[f] = fuel_dist.get(f, 0) + 1

    # 2. Brand distribution
    brand_counts = {}
    for v in all_vehicles:
        b = v.get("brand", "Unknown")
        brand_counts[b] = brand_counts.get(b, 0) + 1

    top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:8]

    # 3. Average prices
    avg_car_price = round(sum([c.get("price_ex_showroom", 0) for c in cars]) / (total_cars if total_cars else 1), 0)
    avg_bike_price = round(sum([b.get("price_ex_showroom", 0) for b in bikes]) / (total_bikes if total_bikes else 1), 0)

    # 4. Mileage stats
    avg_car_mileage = round(sum([c.get("mileage_kmpl", 0) for c in cars]) / (total_cars if total_cars else 1), 1)
    avg_bike_mileage = round(sum([b.get("mileage_kmpl", 0) for b in bikes]) / (total_bikes if total_bikes else 1), 1)

    # 5. Price brackets
    car_price_brackets = {
        "Under 8 Lakh": len([c for c in cars if c.get("price_ex_showroom", 0) < 800000]),
        "8L - 15 Lakh": len([c for c in cars if 800000 <= c.get("price_ex_showroom", 0) < 1500000]),
        "15L - 25 Lakh": len([c for c in cars if 1500000 <= c.get("price_ex_showroom", 0) < 2500000]),
        "Above 25 Lakh": len([c for c in cars if c.get("price_ex_showroom", 0) >= 2500000]),
    }

    bike_price_brackets = {
        "Under 1 Lakh": len([b for b in bikes if b.get("price_ex_showroom", 0) < 100000]),
        "1L - 2 Lakh": len([b for b in bikes if 100000 <= b.get("price_ex_showroom", 0) < 200000]),
        "2L - 3.5 Lakh": len([b for b in bikes if 200000 <= b.get("price_ex_showroom", 0) < 350000]),
        "Above 3.5 Lakh": len([b for b in bikes if b.get("price_ex_showroom", 0) >= 350000]),
    }

    # 6. User and interaction counts
    total_users = await users_col.count_documents({})
    total_interactions = await interactions_col.count_documents({})
    total_recommendations = await recs_col.count_documents({})
    total_predictions = await preds_col.count_documents({})

    return {
        "overview": {
            "total_vehicles": total_vehicles,
            "total_cars": total_cars,
            "total_bikes": total_bikes,
            "total_users": total_users,
            "total_interactions": total_interactions,
            "total_recommendations": total_recommendations,
            "total_predictions": total_predictions
        },
        "averages": {
            "avg_car_price_inr": avg_car_price,
            "avg_bike_price_inr": avg_bike_price,
            "avg_car_mileage_kmpl": avg_car_mileage,
            "avg_bike_mileage_kmpl": avg_bike_mileage
        },
        "charts": {
            "category_split": {"Cars": total_cars, "Bikes": total_bikes},
            "fuel_distribution": fuel_dist,
            "popular_brands": {k: v for k, v in top_brands},
            "car_price_distribution": car_price_brackets,
            "bike_price_distribution": bike_price_brackets
        }
    }
