"""
Inventory Optimization Module
Implements: EOQ, Safety Stock, Reorder Point (ROP), Total Inventory Cost
"""

import pandas as pd
import numpy as np


# ── EOQ Model ─────────────────────────────────────────────────────────────────

def economic_order_quantity(annual_demand, ordering_cost, holding_cost_per_unit):
    """
    EOQ = sqrt(2 * D * S / H)

    Parameters
    ----------
    annual_demand         : D — annual units demanded
    ordering_cost         : S — cost per order placed (₹)
    holding_cost_per_unit : H — holding cost per unit per year (₹)

    Returns
    -------
    eoq : float — optimal order quantity (units)
    """
    if holding_cost_per_unit <= 0:
        return annual_demand  # safety fallback
    eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)
    return round(eoq, 2)


# ── Safety Stock ──────────────────────────────────────────────────────────────

def safety_stock(std_demand, lead_time_days, service_level=0.95):
    """
    Safety Stock = Z * σ_demand * sqrt(Lead Time)

    Parameters
    ----------
    std_demand      : standard deviation of daily demand
    lead_time_days  : supplier lead time in days
    service_level   : desired service level (default 95%)

    Returns
    -------
    ss : float — safety stock units
    """
    z_table = {0.90: 1.28, 0.95: 1.645, 0.98: 2.05, 0.99: 2.33}
    z = z_table.get(service_level, 1.645)
    ss = z * std_demand * np.sqrt(lead_time_days)
    return round(ss, 2)


# ── Reorder Point ─────────────────────────────────────────────────────────────

def reorder_point(avg_daily_demand, lead_time_days, ss):
    """
    ROP = (Average Daily Demand × Lead Time) + Safety Stock

    When inventory hits ROP → place new order immediately.
    """
    rop = (avg_daily_demand * lead_time_days) + ss
    return round(rop, 2)


# ── Total Inventory Cost ──────────────────────────────────────────────────────

def total_inventory_cost(annual_demand, order_qty, ordering_cost, holding_cost_per_unit):
    """
    TC = (D/Q)*S + (Q/2)*H
    """
    if order_qty <= 0:
        return float("inf")
    orders_per_year = annual_demand / order_qty
    ordering = orders_per_year * ordering_cost
    holding  = (order_qty / 2) * holding_cost_per_unit
    return round(ordering + holding, 2)


# ── Master Inventory Table ────────────────────────────────────────────────────

def compute_inventory_parameters(df, ordering_cost=500, holding_rate=0.20, service_level=0.95):
    """
    Compute EOQ, Safety Stock, ROP, and Total Cost for every product.

    Parameters
    ----------
    df              : sales DataFrame (output of generate_sales_data)
    ordering_cost   : fixed cost per order placed (₹) — default ₹500
    holding_rate    : annual holding cost as fraction of unit cost — default 20%
    service_level   : target service level — default 95%

    Returns
    -------
    inv_df : DataFrame with all inventory KPIs per product
    """
    rows = []
    for pid in df["product_id"].unique():
        pdata = df[df["product_id"] == pid].sort_values("date")
        pname      = pdata["product_name"].iloc[0]
        unit_cost  = pdata["unit_cost"].iloc[0]
        lead_days  = pdata["lead_time_days"].iloc[0]

        monthly_demand = pdata["units_sold"].values
        avg_monthly    = np.mean(monthly_demand)
        std_monthly    = np.std(monthly_demand)

        # Convert to daily (approx 30 days/month)
        avg_daily = avg_monthly / 30
        std_daily = std_monthly / 30

        annual_demand = avg_monthly * 12
        H = unit_cost * holding_rate          # holding cost per unit per year

        eoq = economic_order_quantity(annual_demand, ordering_cost, H)
        ss  = safety_stock(std_daily, lead_days, service_level)
        rop = reorder_point(avg_daily, lead_days, ss)
        tc  = total_inventory_cost(annual_demand, eoq, ordering_cost, H)

        # Number of orders per year
        orders_yr = round(annual_demand / eoq, 1) if eoq > 0 else "N/A"
        # Avg cycle time (days)
        cycle_days = round(365 / orders_yr, 1) if isinstance(orders_yr, float) else "N/A"

        rows.append({
            "Product ID":           pid,
            "Product Name":         pname,
            "Avg Monthly Demand":   round(avg_monthly, 0),
            "Annual Demand (units)":round(annual_demand, 0),
            "Unit Cost (Rs)":        unit_cost,
            "Lead Time (days)":     lead_days,
            "EOQ (units)":          eoq,
            "Safety Stock (units)": ss,
            "Reorder Point (units)":rop,
            "Orders/Year":          orders_yr,
            "Cycle Time (days)":    cycle_days,
            "Total Inv Cost (Rs/yr)":tc,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from data.generate_data import generate_sales_data
    df = generate_sales_data()
    inv = compute_inventory_parameters(df)
    print("\n📦 Inventory Optimization Results:")
    print(inv.to_string(index=False))
