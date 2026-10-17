"""
ABC-XYZ Analysis Module
ABC  → classification by Revenue contribution (Pareto Principle)
XYZ  → classification by Demand variability (CoV)
"""

import pandas as pd
import numpy as np


# ── ABC Analysis ──────────────────────────────────────────────────────────────

def abc_analysis(df):
    """
    Classify products into A / B / C based on cumulative revenue share.

    A : top 70% revenue  (high-value, focus items)
    B : next 20% revenue (medium-value)
    C : bottom 10%       (low-value, low priority)

    Returns
    -------
    abc_df : DataFrame sorted by revenue descending with ABC class
    """
    rev = (
        df.groupby(["product_id", "product_name"])["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    total_rev = rev["revenue"].sum()
    rev["revenue_pct"]    = (rev["revenue"] / total_rev * 100).round(2)
    rev["cumulative_pct"] = rev["revenue_pct"].cumsum().round(2)

    def _class(cum):
        if cum <= 70:
            return "A"
        elif cum <= 90:
            return "B"
        else:
            return "C"

    rev["ABC_Class"] = rev["cumulative_pct"].apply(_class)
    return rev.reset_index(drop=True)


# ── XYZ Analysis ──────────────────────────────────────────────────────────────

def xyz_analysis(df):
    """
    Classify products by demand variability using Coefficient of Variation (CoV).

    CoV = (Standard Deviation / Mean) × 100

    X : CoV ≤ 10%   → highly predictable demand
    Y : 10% < CoV ≤ 25% → moderately variable
    Z : CoV > 25%   → highly unpredictable demand

    Returns
    -------
    xyz_df : DataFrame with CoV and XYZ class per product
    """
    stats = (
        df.groupby(["product_id", "product_name"])["units_sold"]
        .agg(["mean", "std"])
        .reset_index()
    )
    stats.columns = ["product_id", "product_name", "mean_demand", "std_demand"]
    stats["CoV_%"] = (stats["std_demand"] / stats["mean_demand"] * 100).round(2)

    def _class(cov):
        if cov <= 10:
            return "X"
        elif cov <= 25:
            return "Y"
        else:
            return "Z"

    stats["XYZ_Class"] = stats["CoV_%"].apply(_class)
    return stats


# ── Combined ABC-XYZ Matrix ───────────────────────────────────────────────────

def abc_xyz_matrix(df):
    """
    Merge ABC and XYZ results into a single classification matrix.

    Returns
    -------
    combined : DataFrame with columns [product_id, product_name,
                revenue, ABC_Class, CoV_%, XYZ_Class, Combined_Class]
    """
    abc = abc_analysis(df)
    xyz = xyz_analysis(df)

    combined = abc.merge(
        xyz[["product_id", "CoV_%", "XYZ_Class", "mean_demand", "std_demand"]],
        on="product_id"
    )

    combined["Combined_Class"] = combined["ABC_Class"] + combined["XYZ_Class"]

    # Strategic recommendation
    strategy_map = {
        "AX": "High value + predictable   -> Keep low safety stock, JIT",
        "AY": "High value + variable      -> Moderate safety stock",
        "AZ": "High value + unpredictable -> High safety stock, close monitoring",
        "BX": "Medium value + predictable -> Standard EOQ",
        "BY": "Medium value + variable    -> Periodic review",
        "BZ": "Medium value + volatile    -> Buffer stock",
        "CX": "Low value + predictable    -> Bulk ordering OK",
        "CY": "Low value + variable       -> Consolidate orders",
        "CZ": "Low value + unpredictable  -> Consider delisting",
    }
    combined["Strategy"] = combined["Combined_Class"].map(strategy_map)

    return combined[[
        "product_id", "product_name", "revenue", "revenue_pct",
        "cumulative_pct", "ABC_Class", "mean_demand", "CoV_%",
        "XYZ_Class", "Combined_Class", "Strategy"
    ]]


if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from data.generate_data import generate_sales_data
    df = generate_sales_data()
    matrix = abc_xyz_matrix(df)
    print("\n🅰️ ABC-XYZ Classification Matrix:")
    print(matrix.to_string(index=False))
