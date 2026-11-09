import pytest
import os
import json
import joblib
import numpy as np
import pandas as pd
from backend.app.config import settings
from backend.app.models.prediction import CarPredictionRequest, BikePredictionRequest
from backend.app.services.prediction_service import prediction_service
from backend.app.services.recommendation_service import recommendation_service

def test_car_ml_model_artifacts_and_inference():
    model_path = os.path.join(settings.ML_MODELS_DIR, "car_price_model.joblib")
    meta_path = os.path.join(settings.ML_MODELS_DIR, "car_model_meta.json")
    assert os.path.exists(model_path)
    assert os.path.exists(meta_path)

    pipeline = joblib.load(model_path)
    assert hasattr(pipeline, "predict")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["test_metrics"]["test_r2"] > 0.90
    assert "preprocessor" in pipeline.named_steps
    assert "regressor" in pipeline.named_steps

    # Test direct inference via service
    req = CarPredictionRequest(
        brand="Hyundai",
        model="Creta",
        year=2021,
        km_driven=35000,
        fuel_type="Diesel",
        transmission="Manual",
        engine_cc=1493.0,
        mileage_kmpl=21.4,
        seller_type="Individual",
        owner="First Owner",
        seats=5
    )
    result = prediction_service.predict_car(req)
    assert result.predicted_price > 600000
    assert result.price_range_low < result.predicted_price < result.price_range_high
    assert len(result.feature_importances) > 0

def test_bike_ml_model_artifacts_and_inference():
    model_path = os.path.join(settings.ML_MODELS_DIR, "bike_price_model.joblib")
    meta_path = os.path.join(settings.ML_MODELS_DIR, "bike_model_meta.json")
    assert os.path.exists(model_path)
    assert os.path.exists(meta_path)

    pipeline = joblib.load(model_path)
    assert hasattr(pipeline, "predict")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["test_metrics"]["test_r2"] > 0.90
    assert "preprocessor" in pipeline.named_steps
    assert "regressor" in pipeline.named_steps

    req = BikePredictionRequest(
        brand="Yamaha",
        model="YZF R15 V3",
        year=2020,
        km_driven=25000,
        engine_cc=155.0,
        mileage_kmpl=48.0,
        seller_type="Individual",
        owner="First Owner"
    )
    result = prediction_service.predict_bike(req)
    assert result.predicted_price > 50000
    assert result.price_range_low < result.predicted_price < result.price_range_high

def test_recommender_hybrid_and_cold_start():
    # Cold start preferences
    prefs = {
        "category": "car",
        "min_budget": 600000,
        "max_budget": 1400000,
        "fuel_types": ["Petrol"],
        "transmissions": ["Manual"],
        "safety_priority": "High",
        "primary_usage": "City",
        "top_k": 5
    }
    recs = recommendation_service.recommend(prefs, user_id=None, top_k=5)
    assert len(recs["recommendations"]) == 5
    assert "Cold-Start" in recs["methodology"] or "Hybrid" in recs["methodology"]
    assert all(r["vehicle"]["category"] == "car" for r in recs["recommendations"])
    assert len(recs["alternatives"]) > 0
