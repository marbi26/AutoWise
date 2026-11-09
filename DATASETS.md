# AutoWise Dataset Documentation & Data Lineage

This document provides complete, transparent documentation of all datasets utilized across the AutoWise recommendation engine, valuation machine learning models, and analytics dashboard.

---

## 1. Dataset Directory Architecture

```
ml/data/
├── raw/
│   ├── metadata.json                         # Provenance, license, and collection date manifests
│   ├── vehicle_catalog_raw.json              # Raw specification records for 57 Indian vehicles
│   ├── used_cars_raw.csv                     # Raw used car transaction records
│   ├── used_bikes_raw.csv                    # Raw used motorcycle transaction records
│   └── user_interactions_raw.csv            # Raw platform interaction logs
├── processed/
│   ├── vehicles_catalog_cleaned.csv          # Standardized specifications (57 records)
│   ├── used_cars_cleaned.csv                 # Cleaned car resale training data (2,941 records)
│   ├── used_bikes_cleaned.csv                # Cleaned motorcycle resale training data (2,456 records)
│   └── user_interactions_cleaned.csv         # Interaction matrix dataset (1,000 logs)
└── seeds/
    └── vehicles_seed.json                    # Database seeding artifact for MongoDB/JSON store
```

---

## 2. Specification Catalog Dataset (`vehicles_catalog_cleaned.csv`)

- **Total Records**: 57 verified Indian production vehicle models (34 Passenger Cars, 23 Two-Wheelers).
- **Collection Date**: February 2026.
- **Sources**:
  - Automotive Research Association of India (ARAI) official fuel economy certifications.
  - Global NCAP (Safer Cars for India campaign) & Bharat NCAP test crash rating records.
  - Manufacturer Ex-Showroom (New Delhi) pricing schedules and technical specification sheets.
- **License**: Public Regulatory & Technical Disclosures (Fair Use for Engineering Research & Educational Placement).

### Schema Attributes:
| Field | Type | Description | Range / Example |
| :--- | :--- | :--- | :--- |
| `vehicle_id` | String | Unique slug identifier | `car_tata_nexon`, `bike_royal_enfield_classic_350` |
| `brand` | String | Manufacturer brand name | Maruti Suzuki, Tata, Hyundai, Royal Enfield |
| `model` | String | Commercial model designation | Nexon, Creta, Swift, Classic 350, Pulsar |
| `variant` | String | Trim / Variant specification | Creative+ S, SX (O), ZXi+ |
| `category` | String | Vehicle domain | `car` or `bike` |
| `price_ex_showroom` | Float | Base ex-showroom price (INR) | ₹64,900 – ₹42,50,000 |
| `on_road_price_est` | Float | Estimated on-road price (INR) | Includes RTO (12%) + Comprehensive Insurance |
| `fuel_type` | String | Powertrain fuel category | Petrol, Diesel, CNG, Electric |
| `transmission` | String | Transmission architecture | Manual, Automatic, AMT, CVT, DCT |
| `body_type` | String | Segment classification | SUV, Hatchback, Sedan, Cruiser, Naked, Commuter |
| `engine_cc` | Float | Engine displacement | 97.2 cc – 2184.0 cc |
| `power_bhp` | Float | Peak power output | 7.9 bhp – 200.0 bhp |
| `torque_nm` | Float | Peak engine torque | 8.05 Nm – 450.0 Nm |
| `mileage_kmpl` | Float | ARAI certified fuel efficiency | 12.8 kmpl – 38.0 km/kg (or 465 km per EV charge) |
| `safety_rating` | Float | Bharat NCAP / Global NCAP Stars | 0.0 – 5.0 |
| `seating_capacity` | Integer | Max passenger capacity | 2 (Bikes), 4–7 (Cars) |
| `boot_space_l` | Float | Luggage boot volume | 170 L – 587 L |
| `fuel_tank_capacity_l`| Float | Fuel capacity (Litres) | 10.0 L – 60.0 L |

---

## 3. Used Car Valuation Training Dataset (`used_cars_cleaned.csv`)

- **Total Records**: 2,941 verified Indian transaction records.
- **Target Variable**: `resale_price_inr` (INR).
- **Features Cleaned & Standardized**:
  - `brand`: Standardized manufacturer names (e.g., Maruti, Hyundai, Tata, Honda, Mahindra, Toyota).
  - `model`: Cleaned model names without variant junk suffixes.
  - `year`: Manufacturing year (2006 to 2024).
  - `km_driven`: Total odometer reading (1,200 km to 2,80,000 km).
  - `fuel_type`: `Petrol`, `Diesel`, `CNG`, `Electric`.
  - `transmission`: `Manual`, `Automatic`.
  - `seller_type`: `Individual`, `Dealer`, `Trustmark Dealer`.
  - `owner`: `First Owner`, `Second Owner`, `Third Owner`, `Fourth & Above Owner`.
  - `mileage_kmpl`: Numeric conversion from "kmpl" / "km/kg" text.
  - `engine_cc`: Displacement converted to float.
  - `max_power_bhp`: Cleaned from string notation to float.
  - `seats`: Verified integer seating count.
- **Engineered Features**:
  - `vehicle_age`: Calculated as `2026 - year`.
  - `km_per_year`: Calculated as `km_driven / vehicle_age`.
- **Handling Outliers & Noise**:
  - Excluded luxury outliers with prices exceeding ₹50,00,000 or impossible odometer readings (>4,00,000 km) to preserve regression stability.
  - Imputed missing displacement and mileage with median values stratified by `(brand, fuel_type)`.

---

## 4. Used Bike Valuation Training Dataset (`used_bikes_cleaned.csv`)

- **Total Records**: 2,456 verified Indian transaction records.
- **Target Variable**: `resale_price_inr` (INR).
- **Features Cleaned & Standardized**:
  - `brand`: Royal Enfield, Hero, Bajaj, TVS, Yamaha, Honda, KTM.
  - `model`: Classic 350, Splendor, Pulsar, Apache, R15, Duke 390, Activa.
  - `year`: Manufacturing year (2008 to 2024).
  - `km_driven`: Verified odometer reading (500 km to 1,50,000 km).
  - `engine_cc`: Displacement (97.2 cc to 648.0 cc).
  - `seller_type`: `Individual`, `Dealer`.
  - `owner`: `First Owner`, `Second Owner`.
- **Engineered Features**:
  - `vehicle_age`: Calculated as `2026 - year`.
  - `km_per_year`: Calculated as `km_driven / vehicle_age`.

---

## 5. User Interaction Behavioral Dataset (`user_interactions_cleaned.csv`)

- **Total Records**: 1,000 interaction entries across 120 unique synthetic user profiles.
- **Attributes**:
  - `user_id`: Unique identifier of user.
  - `vehicle_id`: Unique target vehicle identifier.
  - `interaction_type`: Categorized behavioral events:
    - `view`: Implicit vehicle card detail view (Weight: 1.0).
    - `compare`: Added to side-by-side comparison matrix (Weight: 2.0).
    - `save`: Bookmarked in user dashboard (Weight: 3.0).
    - `like`: Explicit upvote thumbs up (Weight: 4.0).
    - `dislike`: Explicit downvote thumbs down (Weight: -2.0).
  - `rating`: Normalized interaction weight on a 1.0 to 5.0 scale.
  - `timestamp`: ISO-8601 UTC timestamp.
- **Purpose**: Powers Collaborative Filtering user-item interaction matrix and hybrid recommendation scoring.

---

## 6. Preprocessing & Integrity Pipelines

Both datasets undergo a deterministic scikit-learn `Pipeline` utilizing `ColumnTransformer`:
1. **Numerical Pipeline**:
   - `RobustScaler`: Handles heavy-tailed distributions in mileage and odometer readings without being skewed by extreme values.
2. **Categorical Pipeline**:
   - `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`: Encodes discrete categories into orthogonal feature vectors, safely handling unobserved vehicle trims during production inference.
