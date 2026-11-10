import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AutoWise"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"

    # Security
    SECRET_KEY: str = "autowise-super-secret-jwt-key-development-2026-production-ready"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    MONGODB_ENABLED: bool = False
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "autowise_db"
    USE_LOCAL_FALLBACK_IF_NO_MONGO: bool = True

    # Directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ML_MODELS_DIR: str = os.path.join(BASE_DIR, "ml", "models")
    ML_DATA_DIR: str = os.path.join(BASE_DIR, "ml", "data")
    FRONTEND_DIR: str = os.path.join(BASE_DIR, "frontend")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
