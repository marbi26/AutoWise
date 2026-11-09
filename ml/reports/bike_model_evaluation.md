# AutoWise Bike Price Prediction Model Evaluation Report

**Champion Model:** XGBoost Regressor
**Test R²:** 0.9861 | **Test MAE:** ₹2,916 | **RMSE:** ₹4,418

### Model Benchmark Comparison

| Model Algorithm | Test R² | Test MAE (INR) | Test RMSE (INR) | 5-Fold CV R² |
| :--- | :--- | :--- | :--- | :--- |
| Linear Regression | 0.8892 | ₹8,930 | ₹12,453 | 0.8841 |
| Ridge Regression | 0.8892 | ₹8,920 | ₹12,456 | 0.8843 |
| Lasso Regression | 0.8888 | ₹8,898 | ₹12,477 | 0.8844 |
| Decision Tree | 0.9416 | ₹5,909 | ₹9,039 | 0.9342 |
| Random Forest | 0.9699 | ₹4,009 | ₹6,490 | 0.9699 |
| XGBoost Regressor | 0.9861 | ₹2,916 | ₹4,418 | 0.9843 |

### Feature Importance Breakdown

| Feature | Relative Importance (%) |
| :--- | :--- |
| `model` | 28.31% |
| `brand` | 17.2% |
| `engine_cc` | 15.08% |
| `year` | 12.39% |
| `vehicle_age` | 10.39% |
| `mileage_kmpl` | 8.58% |
| `owner` | 6.32% |
| `km_driven` | 1.48% |
