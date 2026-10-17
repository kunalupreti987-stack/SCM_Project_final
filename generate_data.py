"""
Data Generator for FMCG Supply Chain Project
Generates realistic synthetic sales data for TCPL-like FMCG products
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)

# ── Product Catalog ──────────────────────────────────────────────────────────
PRODUCTS = {
    "P001": {"name": "Tata Tea Premium 250g",  "category": "Tea",    "unit_price": 65,   "unit_cost": 42},
    "P002": {"name": "Tata Tea Premium 500g",  "category": "Tea",    "unit_price": 120,  "unit_cost": 78},
    "P003": {"name": "Tata Tea Gold 250g",     "category": "Tea",    "unit_price": 80,   "unit_cost": 52},
    "P004": {"name": "Tetley Green Tea 100TB", "category": "Tea",    "unit_price": 150,  "unit_cost": 95},
    "P005": {"name": "Tata Salt 1kg",          "category": "Salt",   "unit_price": 22,   "unit_cost": 14},
    "P006": {"name": "Tata Salt Lite 1kg",     "category": "Salt",   "unit_price": 28,   "unit_cost": 18},
    "P007": {"name": "Tata Sampann Dal 500g",  "category": "Food",   "unit_price": 75,   "unit_cost": 50},
    "P008": {"name": "Tata Sampann Chana Dal", "category": "Food",   "unit_price": 85,   "unit_cost": 55},
    "P009": {"name": "Himalayan Water 500ml",  "category": "Water",  "unit_price": 20,   "unit_cost": 8},
    "P010": {"name": "Eight O Clock Coffee",   "category": "Coffee", "unit_price": 250,  "unit_cost": 160},
}

# ── Seasonal Factors (monthly index 1–12) ────────────────────────────────────
SEASONAL = {
    "Tea":    [1.3, 1.2, 1.1, 0.9, 0.8, 0.7, 0.8, 0.9, 1.0, 1.1, 1.3, 1.4],
    "Salt":   [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    "Food":   [1.1, 1.0, 1.0, 1.0, 1.2, 1.2, 1.1, 1.0, 1.0, 1.0, 1.1, 1.2],
    "Water":  [0.7, 0.7, 0.9, 1.1, 1.4, 1.5, 1.5, 1.4, 1.2, 0.9, 0.8, 0.7],
    "Coffee": [1.1, 1.0, 1.0, 0.9, 0.8, 0.8, 0.9, 1.0, 1.0, 1.1, 1.2, 1.2],
}

# Base monthly demand (units) per product
BASE_DEMAND = {
    "P001": 4500, "P002": 3200, "P003": 2800, "P004": 1500,
    "P005": 6000, "P006": 2000, "P007": 2500, "P008": 1800,
    "P009": 5000, "P010": 800,
}

# Lead time (days) per product
LEAD_TIME = {
    "P001": 7,  "P002": 7,  "P003": 7,  "P004": 10,
    "P005": 5,  "P006": 5,  "P007": 8,  "P008": 8,
    "P009": 3,  "P010": 12,
}


def generate_sales_data(start="2024-01-01", months=24):
    """Generate monthly sales data for all products."""
    records = []
    start_dt = datetime.strptime(start, "%Y-%m-%d")

    for pid, info in PRODUCTS.items():
        cat = info["category"]
        base = BASE_DEMAND[pid]
        trend = 1.0  # cumulative growth factor

        for m in range(months):
            date = start_dt + timedelta(days=30 * m)
            month_idx = date.month - 1  # 0-based
            trend += 0.005  # 0.5% monthly growth

            seasonal = SEASONAL[cat][month_idx]
            noise = np.random.normal(1.0, 0.08)  # ±8% random variation
            demand = max(0, int(base * trend * seasonal * noise))

            records.append({
                "date":        date.strftime("%Y-%m-%d"),
                "product_id":  pid,
                "product_name": info["name"],
                "category":    cat,
                "units_sold":  demand,
                "unit_price":  info["unit_price"],
                "unit_cost":   info["unit_cost"],
                "revenue":     demand * info["unit_price"],
                "lead_time_days": LEAD_TIME[pid],
            })

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_sales_data()
    df.to_csv("data/fmcg_sales_data.csv", index=False)
    print(f"✅ Dataset generated: {df.shape[0]} rows × {df.shape[1]} cols")
    print(df.head(10).to_string(index=False))
