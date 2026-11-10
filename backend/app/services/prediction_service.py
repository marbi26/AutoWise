import os
import json
import joblib
import pandas as pd
import numpy as np

from backend.app.config import settings
from backend.app.models.prediction import CarPredictionRequest, BikePredictionRequest, PredictionResponse, FeatureImpact

class PredictionService:
    def __init__(self):
        self.car_model_path = os.path.join(settings.ML_MODELS_DIR, "car_price_model.joblib")
        self.car_meta_path = os.path.join(settings.ML_MODELS_DIR, "car_model_meta.json")
        self.bike_model_path = os.path.join(settings.ML_MODELS_DIR, "bike_price_model.joblib")
        self.bike_meta_path = os.path.join(settings.ML_MODELS_DIR, "bike_model_meta.json")

        self.car_model = None
        self.car_meta = {}
        self.bike_model = None
        self.bike_meta = {}

        self.load_models()

    def load_models(self):
        if os.path.exists(self.car_model_path):
            self.car_model = joblib.load(self.car_model_path)
        if os.path.exists(self.car_meta_path):
            with open(self.car_meta_path, "r") as f:
                self.car_meta = json.load(f)

        if os.path.exists(self.bike_model_path):
            self.bike_model = joblib.load(self.bike_model_path)
        if os.path.exists(self.bike_meta_path):
            with open(self.bike_meta_path, "r") as f:
                self.bike_meta = json.load(f)

    def predict_car(self, req: CarPredictionRequest) -> PredictionResponse:
        current_year = 2026
        age = max(1, current_year - req.year)
        km_per_year = round(req.km_driven / age, 1)

        input_data = pd.DataFrame([{
            "brand": req.brand,
            "model": req.model,
            "fuel_type": req.fuel_type,
            "transmission": req.transmission,
            "seller_type": req.seller_type or "Individual",
            "owner": req.owner or "First Owner",
            "year": req.year,
            "km_driven": req.km_driven,
            "mileage_kmpl": req.mileage_kmpl or 18.0,
            "engine_cc": req.engine_cc or 1200.0,
            "seats": req.seats or 5,
            "vehicle_age": age,
            "km_per_year": km_per_year
        }])

        raw_pred = float(self.car_model.predict(input_data)[0])
        pred_price = max(50000.0, round(raw_pred, -3))

        # Statistical 95% Confidence Interval using residual standard error
        std = self.car_meta.get("residual_std", 50000.0)
        margin = 1.96 * std
        low = max(50000.0, round(pred_price - margin, -3))
        high = round(pred_price + margin, -3)

        top_feats = [
            FeatureImpact(feature=f["feature"], importance_percentage=f["importance_percentage"])
            for f in self.car_meta.get("top_features", [])
        ]

        metrics = self.car_meta.get("test_metrics", {})
        return PredictionResponse(
            category="car",
            predicted_price=pred_price,
            price_range_low=low,
            price_range_high=high,
            confidence_interval_percentage=95.0,
            model_name=self.car_meta.get("champion_algorithm", "XGBoost Regressor"),
            model_r2_score=metrics.get("test_r2", 0.98),
            model_mae_inr=metrics.get("test_mae", 30000.0),
            feature_importances=top_feats,
            disclaimer="Estimates are computed using AutoWise's machine learning model trained on Indian used car market data. Physical condition, service records, and local market factors may influence final realized price."
        )

    def predict_bike(self, req: BikePredictionRequest) -> PredictionResponse:
        current_year = 2026
        age = max(1, current_year - req.year)
        km_per_year = round(req.km_driven / age, 1)

        input_data = pd.DataFrame([{
            "brand": req.brand,
            "model": req.model,
            "seller_type": req.seller_type or "Individual",
            "owner": req.owner or "First Owner",
            "year": req.year,
            "km_driven": req.km_driven,
            "mileage_kmpl": req.mileage_kmpl or 40.0,
            "engine_cc": req.engine_cc or 150.0,
            "vehicle_age": age,
            "km_per_year": km_per_year
        }])

        raw_pred = float(self.bike_model.predict(input_data)[0])
        pred_price = max(10000.0, round(raw_pred, -2))

        std = self.bike_meta.get("residual_std", 4500.0)
        margin = 1.96 * std
        low = max(10000.0, round(pred_price - margin, -2))
        high = round(pred_price + margin, -2)

        top_feats = [
            FeatureImpact(feature=f["feature"], importance_percentage=f["importance_percentage"])
            for f in self.bike_meta.get("top_features", [])
        ]

        metrics = self.bike_meta.get("test_metrics", {})
        return PredictionResponse(
            category="bike",
            predicted_price=pred_price,
            price_range_low=low,
            price_range_high=high,
            confidence_interval_percentage=95.0,
            model_name=self.bike_meta.get("champion_algorithm", "XGBoost Regressor"),
            model_r2_score=metrics.get("test_r2", 0.98),
            model_mae_inr=metrics.get("test_mae", 3000.0),
            feature_importances=top_feats,
            disclaimer="Estimates are generated by AutoWise's machine learning model calibrated against Indian used two-wheeler market sales. Actual resale is subject to mechanical inspection, tyre wear, and cosmetic condition."
        )

    def get_meta(self):
        return {
            "car_model": self.car_meta,
            "bike_model": self.bike_meta
        }

prediction_service = PredictionService()
