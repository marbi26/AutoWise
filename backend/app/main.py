import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import db_manager

# Routers
from backend.app.routers import (
    auth,
    vehicles,
    recommendations,
    prediction,
    compare,
    ownership,
    analytics,
    interactions
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB and seed catalog
    print(f"Starting {settings.APP_NAME} Backend Engine...")
    await db_manager.connect()
    yield
    print(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title="AutoWise API",
    description="Intelligent Indian Vehicle Recommendation & Machine Learning Valuation Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(recommendations.router)
app.include_router(prediction.router)
app.include_router(compare.router)
app.include_router(ownership.router)
app.include_router(analytics.router)
app.include_router(interactions.router)

# Health Check
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database": "mongodb" if db_manager.is_mongodb_connected else "resilient_json_store"
    }

# Mount Static Frontend
frontend_path = os.path.join(settings.BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    @app.get("/{page_name}.html", include_in_schema=False)
    async def serve_html_pages(page_name: str):
        target = os.path.join(frontend_path, f"{page_name}.html")
        if os.path.exists(target):
            return FileResponse(target)
        return FileResponse(os.path.join(frontend_path, "index.html"))
