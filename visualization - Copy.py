# -*- coding: utf-8 -*-
"""
Visualization Module
All charts and dashboards for the Supply Chain project
Saves plots to outputs/ directory
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore")
os.makedirs("outputs", exist_ok=True)

COLORS = {
    "A": "#e74c3c", "B": "#f39c12", "C": "#2ecc71",
    "X": "#3498db", "Y": "#9b59b6", "Z": "#e67e22",
}

SAVE_MSG = "[OK] Saved: {}"


# --- 1. Monthly Sales Trend ---

def plot_sales_trend(df, top_n=5, save=True):
    """Line chart: monthly sales trend for top-N products."""
    top_prods = (
        df.groupby("product_id")["revenue"].sum()
        .nlargest(top_n).index
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    for pid in top_prods:
        pdata = df[df["product_id"] == pid].sort_values("date")
        pname = pdata["product_name"].iloc[0]
        ax.plot(pdata["date"], pdata["units_sold"], marker="o",
                markersize=4, linewidth=2, label=pname)

    ax.set_title("Monthly Sales Trend - Top 5 Products (TCPL Portfolio)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Units Sold", fontsize=11)
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    if save:
        path = "outputs/1_sales_trend.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(SAVE_MSG.format(path))
    plt.close(fig)


# --- 2. Demand Forecast Chart ---

def plot_forecast(df, forecast_dict, pid="P001", save=True):
    """Actual vs ARIMA Forecast for one product."""
    pdata = df[df["product_id"] == pid].sort_values("date")
    pname = pdata["product_name"].iloc[0]

    actual_dates  = list(pdata["date"])
    actual_values = list(pdata["units_sold"])

    last_date    = actual_dates[-1]
    future_dates = [last_date + pd.DateOffset(months=i+1) for i in range(3)]
    future_vals  = forecast_dict.get(pid, [])

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(actual_dates, actual_values, color="#2c3e50",
            linewidth=2, label="Actual Demand", zorder=3)

    if future_vals:
        ax.plot([actual_dates[-1]] + future_dates,
                [actual_values[-1]] + list(future_vals),
                color="#e74c3c", linewidth=2, linestyle="--",
                marker="D", markersize=7, label="ARIMA Forecast")

        fvals = np.array(future_vals, dtype=float)
        ax.fill_between(
            future_dates,
            fvals * 0.90, fvals * 1.10,
            color="#e74c3c", alpha=0.15, label="+/- 10% Confidence Band"
        )

    ax.axvline(x=actual_dates[-1], color="gray", linestyle=":", linewidth=1.5)
    ax.text(actual_dates[-1], ax.get_ylim()[1] * 0.95,
            " Forecast ->", color="gray", fontsize=9)
    ax.set_title("Demand Forecast - {}".format(pname), fontsize=13, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Units Sold")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    if save:
        path = "outputs/2_demand_forecast.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(SAVE_MSG.format(path))
    plt.close(fig)


# --- 3. Inventory Dashboard ---

def plot_inventory_dashboard(inv_df, save=True):
    """Bar charts for EOQ, Safety Stock, and ROP per product."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    names = [n.replace(" ", "\n") for n in inv_df["Product Name"]]

    metrics = [
        ("EOQ (units)",          "Optimal Order Qty (EOQ)",  "Units", "#3498db"),
        ("Safety Stock (units)", "Safety Stock (95% SL)",    "Units", "#e74c3c"),
        ("Reorder Point (units)","Reorder Point (ROP)",      "Units", "#2ecc71"),
    ]

    for ax, (col, title, ylabel, color) in zip(axes, metrics):
        vals = inv_df[col].astype(float)
        bars = ax.bar(names, vals, color=color, edgecolor="white",
                      linewidth=0.8, alpha=0.85)
        ax.bar_label(bars, fmt="%.0f", fontsize=8, padding=3)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=10)
        ax.tick_params(axis="x", labelsize=7)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.suptitle("Inventory Optimization Dashboard - TCPL Products",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    if save:
        path = "outputs/3_inventory_dashboard.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(SAVE_MSG.format(path))
    plt.close(fig)


# --- 4. ABC Pareto Chart ---

def plot_abc_pareto(abc_df, save=True):
    """Classic Pareto chart for ABC analysis."""
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()

    color_map  = {"A": "#e74c3c", "B": "#f39c12", "C": "#2ecc71"}
    bar_colors = [color_map[c] for c in abc_df["ABC_Class"]]
    names      = [n.replace(" ", "\n") for n in abc_df["product_name"]]

    ax1.bar(names, abc_df["revenue"] / 1e6, color=bar_colors,
            edgecolor="white", linewidth=0.8, alpha=0.85)
    ax2.plot(names, abc_df["cumulative_pct"], color="#2c3e50",
             marker="o", linewidth=2, markersize=6, zorder=5)
    ax2.axhline(70, color="#e74c3c", linestyle="--", alpha=0.6, linewidth=1.2)
    ax2.axhline(90, color="#f39c12", linestyle="--", alpha=0.6, linewidth=1.2)
    ax2.text(len(abc_df) - 0.5, 71, "70% (A|B)", color="#e74c3c", fontsize=8)
    ax2.text(len(abc_df) - 0.5, 91, "90% (B|C)", color="#f39c12", fontsize=8)

    ax1.set_title("ABC Analysis - Pareto Chart (Revenue Contribution)",
                  fontsize=13, fontweight="bold")
    ax1.set_ylabel("Revenue (Rs Million)", fontsize=11)
    ax2.set_ylabel("Cumulative Revenue %", fontsize=11)
    ax1.tick_params(axis="x", labelsize=8)
    legend = [mpatches.Patch(color=v, label="Class {}".format(k))
              for k, v in color_map.items()]
    ax1.legend(handles=legend, loc="upper right")
    fig.tight_layout()
    if save:
        path = "outputs/4_abc_pareto.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(SAVE_MSG.format(path))
    plt.close(fig)


# --- 5. ABC-XYZ Heat Matrix ---

def plot_abc_xyz_heatmap(matrix_df, save=True):
    """Grid heatmap showing ABC-XYZ class distribution."""
    abc_classes = ["A", "B", "C"]
    xyz_classes = ["X", "Y", "Z"]

    fig, ax = plt.subplots(figsize=(9, 7))

    for i, abc in enumerate(abc_classes):
        for j, xyz in enumerate(xyz_classes):
            intensity = (i + j) / 4
            color = plt.cm.RdYlGn_r(intensity)
            rect = plt.Rectangle([j, 2 - i], 1, 1, color=color, alpha=0.7)
            ax.add_patch(rect)

            prods = matrix_df[
                (matrix_df["ABC_Class"] == abc) & (matrix_df["XYZ_Class"] == xyz)
            ]["product_name"].tolist()
            label = "\n".join([p[:20] for p in prods]) if prods else "-"
            ax.text(j + 0.5, 2 - i + 0.5, label,
                    ha="center", va="center", fontsize=8, fontweight="bold",
                    color="black")

    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.set_xticks([0.5, 1.5, 2.5])
    ax.set_xticklabels(["X\n(Stable)", "Y\n(Variable)", "Z\n(Unpredictable)"], fontsize=11)
    ax.set_yticks([0.5, 1.5, 2.5])
    ax.set_yticklabels(["C\n(Low)", "B\n(Medium)", "A\n(High)"], fontsize=11)
    ax.set_xlabel("Demand Variability (XYZ)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Revenue Contribution (ABC)", fontsize=12, fontweight="bold")
    ax.set_title("ABC-XYZ Classification Matrix - TCPL Products",
                 fontsize=13, fontweight="bold", pad=15)
    ax.grid(True, linewidth=1.5, color="white")
    fig.tight_layout()
    if save:
        path = "outputs/5_abc_xyz_matrix.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(SAVE_MSG.format(path))
    plt.close(fig)


# --- 6. Cost Comparison Chart ---

def plot_cost_comparison(inv_df, save=True):
    """Compare Total Inventory Cost across products."""
    fig, ax = plt.subplots(figsize=(14, 6))
    names = [n[:22] for n in inv_df["Product Name"]]
    costs = inv_df["Total Inv Cost (Rs/yr)"].astype(float) / 1000

    bars = ax.barh(names, costs,
                   color=plt.cm.Blues(np.linspace(0.4, 0.9, len(names))))
    ax.bar_label(bars, fmt="Rs %.0fK", fontsize=9, padding=5)
    ax.set_title("Annual Total Inventory Cost per Product (Rs Thousands)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Total Cost (Rs Thousands / year)", fontsize=11)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    fig.tight_layout()
    if save:
        path = "outputs/6_cost_comparison.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(SAVE_MSG.format(path))
    plt.close(fig)


# --- 7. Seasonal Heatmap ---

def plot_seasonal_heatmap(df, save=True):
    """Heatmap of average monthly demand per product."""
    pivot = df.copy()
    pivot["month_name"] = pivot["date"].dt.strftime("%b")

    heat = pivot.pivot_table(
        index="product_name", columns="month_name",
        values="units_sold", aggfunc="mean"
    )
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    heat = heat[[m for m in month_order if m in heat.columns]]

    fig, ax = plt.subplots(figsize=(16, 7))
    im = ax.imshow(heat.values, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(range(len(heat.columns)))
    ax.set_xticklabels(heat.columns, fontsize=10)
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels([n[:25] for n in heat.index], fontsize=9)

    for i in range(len(heat.index)):
        for j in range(len(heat.columns)):
            val = heat.values[i, j]
            txt_color = "black" if val < heat.values.max() * 0.6 else "white"
            ax.text(j, i, "{:,}".format(int(val)),
                    ha="center", va="center", fontsize=8, color=txt_color)

    plt.colorbar(im, ax=ax, label="Avg Units Sold")
    ax.set_title("Seasonal Demand Heatmap - TCPL Products",
                 fontsize=13, fontweight="bold", pad=15)
    fig.tight_layout()
    if save:
        path = "outputs/7_seasonal_heatmap.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(SAVE_MSG.format(path))
    plt.close(fig)
