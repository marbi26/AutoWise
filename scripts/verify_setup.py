import sys

def verify():
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")

    modules = [
        "fastapi", "uvicorn", "pydantic", "pydantic_settings",
        "xgboost", "shap", "pymongo", "motor", "jwt", "bcrypt",
        "sklearn", "pandas", "numpy", "matplotlib", "seaborn",
        "joblib", "httpx", "pytest"
    ]

    for mod in modules:
        try:
            m = __import__(mod)
            v = getattr(m, "__version__", "installed")
            print(f"✓ {mod}: {v}")
        except Exception as e:
            print(f"✗ {mod}: ERROR {e}")

if __name__ == "__main__":
    verify()
