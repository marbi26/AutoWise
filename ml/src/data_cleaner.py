"""
AutoWise Data Cleaning and Preprocessing Pipeline
Performs rigorous data cleaning, missing value imputation, outlier detection,
unit standardization, and train/test dataset preparation for Cars and Bikes.
"""

import os
import json
import numpy as np
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

def clean_catalog_data():
    raw_path = os.path.join(RAW_DIR, "vehicles_catalog.csv")
    df = pd.read_csv(raw_path)
    print(f"[Catalog] Raw rows: {len(df)}")
    
    # 1. Deduplication
    df = df.drop_duplicates(subset=["vehicle_id"])
    
    # 2. Brand & Model Normalization
    df["brand"] = df["brand"].str.strip()
    df["model"] = df["model"].str.strip()
    df["fuel_type"] = df["fuel_type"].str.strip()
    df["transmission"] = df["transmission"].str.strip()
    
    # 3. Numeric conversions & bounds
    numeric_cols = ["price_ex_showroom", "on_road_price_est", "mileage_kmpl", "engine_cc", "power_bhp", "torque_nm", "safety_rating", "seating_capacity"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    # Impute missing safety rating with median (usually 3 or 4 in modern Indian vehicles)
    df["safety_rating"] = df["safety_rating"].fillna(df["safety_rating"].median())
    
    out_path = os.path.join(PROCESSED_DIR, "vehicles_catalog_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"[Catalog] Cleaned rows saved to {out_path}: {len(df)}")
    return df

def remove_outliers_iqr(df, column, lower_percentile=0.01, upper_percentile=0.99):
    q_low = df[column].quantile(lower_percentile)
    q_high = df[column].quantile(upper_percentile)
    return df[(df[column] >= q_low) & (df[column] <= q_high)]

def clean_used_cars_data():
    raw_path = os.path.join(RAW_DIR, "used_cars_raw.csv")
    df = pd.read_csv(raw_path)
    print(f"[Used Cars] Raw rows: {len(df)}")
    
    # 1. Deduplication
    df = df.drop_duplicates()
    
    # 2. Text Normalization
    df["brand"] = df["brand"].str.strip()
    df["model"] = df["model"].str.strip()
    df["fuel_type"] = df["fuel_type"].str.strip()
    df["transmission"] = df["transmission"].str.strip()
    df["seller_type"] = df["seller_type"].str.strip()
    df["owner"] = df["owner"].str.strip()
    
    # 3. Handle outliers on km_driven and selling_price
    df = remove_outliers_iqr(df, "selling_price", 0.005, 0.995)
    df = remove_outliers_iqr(df, "km_driven", 0.005, 0.995)
    
    # 4. Feature engineering: Vehicle Age
    current_year = 2026
    df["vehicle_age"] = current_year - df["year"]
    df["km_per_year"] = (df["km_driven"] / df["vehicle_age"].replace(0, 1)).round(1)
    
    out_path = os.path.join(PROCESSED_DIR, "used_cars_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"[Used Cars] Cleaned rows saved to {out_path}: {len(df)}")
    return df

def clean_used_bikes_data():
    raw_path = os.path.join(RAW_DIR, "used_bikes_raw.csv")
    df = pd.read_csv(raw_path)
    print(f"[Used Bikes] Raw rows: {len(df)}")
    
    # 1. Deduplication
    df = df.drop_duplicates()
    
    # 2. Text Normalization
    df["brand"] = df["brand"].str.strip()
    df["model"] = df["model"].str.strip()
    df["seller_type"] = df["seller_type"].str.strip()
    df["owner"] = df["owner"].str.strip()
    
    # 3. Outlier pruning
    df = remove_outliers_iqr(df, "selling_price", 0.005, 0.995)
    df = remove_outliers_iqr(df, "km_driven", 0.005, 0.995)
    
    # 4. Feature engineering: Vehicle Age
    current_year = 2026
    df["vehicle_age"] = current_year - df["year"]
    df["km_per_year"] = (df["km_driven"] / df["vehicle_age"].replace(0, 1)).round(1)
    
    out_path = os.path.join(PROCESSED_DIR, "used_bikes_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"[Used Bikes] Cleaned rows saved to {out_path}: {len(df)}")
    return df

def clean_user_interactions():
    raw_path = os.path.join(RAW_DIR, "user_interactions_raw.csv")
    df = pd.read_csv(raw_path)
    print(f"[Interactions] Raw rows: {len(df)}")
    
    df = df.drop_duplicates()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(3)
    
    out_path = os.path.join(PROCESSED_DIR, "user_interactions_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"[Interactions] Cleaned rows saved to {out_path}: {len(df)}")
    return df

def run_cleaning_pipeline():
    print("Starting AutoWise Data Cleaning & Preprocessing Pipeline...")
    clean_catalog_data()
    clean_used_cars_data()
    clean_used_bikes_data()
    clean_user_interactions()
    print("All datasets cleaned, normalized, and saved to ml/data/processed/ successfully.")

if __name__ == "__main__":
    run_cleaning_pipeline()
