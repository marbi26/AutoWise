# AutoWise Car Price Prediction Model Evaluation Report

**Champion Model:** XGBoost Regressor
**Test R²:** 0.9857 | **Test MAE:** ₹30,341 | **RMSE:** ₹51,786

### Model Benchmark Comparison

| Model Algorithm | Test R² | Test MAE (INR) | Test RMSE (INR) | 5-Fold CV R² |
| :--- | :--- | :--- | :--- | :--- |
| Linear Regression | 0.8608 | ₹100,411 | ₹161,593 | 0.8701 |
| Ridge Regression | 0.8597 | ₹100,682 | ₹162,242 | 0.8696 |
| Lasso Regression | 0.8601 | ₹100,593 | ₹162,030 | 0.8698 |
| Decision Tree | 0.9628 | ₹56,005 | ₹83,570 | 0.9361 |
| Random Forest | 0.9763 | ₹39,723 | ₹66,660 | 0.9728 |
| XGBoost Regressor | 0.9857 | ₹30,341 | ₹51,786 | 0.9845 |

### Feature Importance Breakdown

| Feature | Relative Importance (%) |
| :--- | :--- |
| `model` | 31.68% |
| `engine_cc` | 23.75% |
| `fuel_type` | 13.14% |
| `vehicle_age` | 10.36% |
| `year` | 6.0% |
| `brand` | 5.58% |
| `transmission` | 4.48% |
| `owner` | 2.56% |
| `mileage_kmpl` | 1.01% |
| `seats` | 0.71% |
| `km_driven` | 0.6% |
