import pytest
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import db_manager
import asyncio

@pytest.fixture(scope="session", autouse=True)
def init_db():
    """Ensure database connection and seeds are loaded for test session."""
    asyncio.run(db_manager.connect())
    yield

@pytest.fixture(scope="session")
def client():
    """Provide a TestClient for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client
