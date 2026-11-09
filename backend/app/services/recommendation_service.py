import os
from ml.src.recommender import AutoWiseRecommender
from backend.app.config import settings

class RecommendationService:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            catalog_path = os.path.join(settings.ML_DATA_DIR, "processed", "vehicles_catalog_cleaned.csv")
            interactions_path = os.path.join(settings.ML_DATA_DIR, "processed", "user_interactions_cleaned.csv")
            cls._instance = AutoWiseRecommender(catalog_path, interactions_path)
        return cls._instance

recommendation_service = RecommendationService.get_instance()
