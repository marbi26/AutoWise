"""
AutoWise Bike Price Prediction Training & Benchmarking Pipeline
Experiments with:
- Linear Regression
- Ridge Regression
- Lasso Regression
- Decision Tree Regressor
- Random Forest Regressor
- XGBoost Regressor

Evaluates MAE, RMSE, R², 5-Fold Cross Validation.
Computes feature importances and residual error bounds for prediction intervals.
Saves model artifacts and comprehensive evaluation reports.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def train_and_evaluate_bikes():
    data_path = os.path.join(DATA_DIR, "used_bikes_cleaned.csv")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} bike records for training.")

    target = "selling_price"
    categorical_features = ["brand", "model", "seller_type", "owner"]
    numerical_features = ["year", "km_driven", "mileage_kmpl", "engine_cc", "vehicle_age", "km_per_year"]

    X = df[categorical_features + numerical_features]
    y = df[target]

    # 80/20 train/test split with fixed seed to prevent leakage
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", RobustScaler(), numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ],
        remainder="drop"
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Lasso Regression": Lasso(alpha=20.0, max_iter=2000),
        "Decision Tree": DecisionTreeRegressor(max_depth=10, min_samples_split=8, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=150, max_depth=14, min_samples_split=4, random_state=42, n_jobs=-1),
        "XGBoost Regressor": XGBRegressor(n_estimators=160, learning_rate=0.08, max_depth=6, subsample=0.85, colsample_bytree=0.85, random_state=42)
    }

    results = {}
    fitted_pipelines = {}
    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    print("\n--- Bike Price Model Comparison Benchmarks ---")
    for name, model in models.items():
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])

        # 5-Fold Cross Validation on Training Data
        cv_scores = cross_validate(
            pipe, X_train, y_train, cv=cv,
            scoring=["neg_mean_absolute_error", "neg_root_mean_squared_error", "r2"]
        )

        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        results[name] = {
            "test_r2": round(float(r2), 4),
            "test_mae": round(float(mae), 2),
            "test_rmse": round(float(rmse), 2),
            "cv_r2_mean": round(float(np.mean(cv_scores["test_r2"])), 4),
            "cv_mae_mean": round(float(-np.mean(cv_scores["test_neg_mean_absolute_error"])), 2),
            "cv_rmse_mean": round(float(-np.mean(cv_scores["test_neg_root_mean_squared_error"])), 2)
        }
        fitted_pipelines[name] = pipe
        print(f"[{name}] R²: {r2:.4f} | MAE: ₹{mae:,.0f} | RMSE: ₹{rmse:,.0f} | CV R²: {np.mean(cv_scores['test_r2']):.4f}")

    # Select champion
    best_model_name = max(results, key=lambda k: results[k]["test_r2"])
    champion_pipeline = fitted_pipelines[best_model_name]
    print(f"\nChampion Bike Model Selected: {best_model_name} (R² = {results[best_model_name]['test_r2']:.4f})")

    # Residuals for confidence intervals
    test_residuals = y_test - champion_pipeline.predict(X_test)
    residual_std = float(np.std(test_residuals))

    # Feature importances
    feature_names = []
    feature_names.extend(numerical_features)
    ohe = champion_pipeline.named_steps["preprocessor"].named_transformers_["cat"]
    ohe_cols = ohe.get_feature_names_out(categorical_features).tolist()
    feature_names.extend(ohe_cols)

    importances = []
    regressor = champion_pipeline.named_steps["regressor"]
    if hasattr(regressor, "feature_importances_"):
        raw_imp = regressor.feature_importances_
        agg_importance = {feat: 0.0 for feat in categorical_features + numerical_features}
        for fname, val in zip(feature_names, raw_imp):
            matched = False
            for base in categorical_features + numerical_features:
                if fname.startswith(base):
                    agg_importance[base] += float(val)
                    matched = True
                    break
            if not matched:
                agg_importance["other"] = agg_importance.get("other", 0.0) + float(val)
        
        total_imp = sum(agg_importance.values())
        importances = [
            {"feature": k, "importance_percentage": round(v / total_imp * 100, 2)}
            for k, v in sorted(agg_importance.items(), key=lambda x: x[1], reverse=True)
            if v > 0.005
        ]

    meta = {
        "model_type": "Bike Price Prediction",
        "champion_algorithm": best_model_name,
        "test_metrics": results[best_model_name],
        "residual_std": round(residual_std, 2),
        "categorical_features": categorical_features,
        "numerical_features": numerical_features,
        "top_features": importances,
        "benchmarks": results,
        "target_currency": "INR",
        "trained_samples": len(X_train),
        "test_samples": len(X_test)
    }

    model_save_path = os.path.join(MODELS_DIR, "bike_price_model.joblib")
    meta_save_path = os.path.join(MODELS_DIR, "bike_model_meta.json")
    joblib.dump(champion_pipeline, model_save_path)
    with open(meta_save_path, "w") as f:
        json.dump(meta, f, indent=2)

    report_md_path = os.path.join(REPORTS_DIR, "bike_model_evaluation.md")
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# AutoWise Bike Price Prediction Model Evaluation Report\n\n")
        f.write(f"**Champion Model:** {best_model_name}\n")
        f.write(f"**Test R²:** {results[best_model_name]['test_r2']} | **Test MAE:** ₹{results[best_model_name]['test_mae']:,.0f} | **RMSE:** ₹{results[best_model_name]['test_rmse']:,.0f}\n\n")
        f.write("### Model Benchmark Comparison\n\n")
        f.write("| Model Algorithm | Test R² | Test MAE (INR) | Test RMSE (INR) | 5-Fold CV R² |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for m_name, m_res in results.items():
            f.write(f"| {m_name} | {m_res['test_r2']} | ₹{m_res['test_mae']:,.0f} | ₹{m_res['test_rmse']:,.0f} | {m_res['cv_r2_mean']} |\n")
        f.write("\n### Feature Importance Breakdown\n\n")
        f.write("| Feature | Relative Importance (%) |\n")
        f.write("| :--- | :--- |\n")
        for fi in importances:
            f.write(f"| `{fi['feature']}` | {fi['importance_percentage']}% |\n")

    print(f"\n✓ Saved model to: {model_save_path}")
    print(f"✓ Saved meta to: {meta_save_path}")
    print(f"✓ Saved report to: {report_md_path}")
    return meta

if __name__ == "__main__":
    train_and_evaluate_bikes()
