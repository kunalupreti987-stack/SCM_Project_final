"""
Demand Forecasting Module
Uses Moving Average + ARIMA for monthly demand prediction per product
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    print("[WARNING] statsmodels not found - using Moving Average fallback.")


# ── Utility ───────────────────────────────────────────────────────────────────

def mape(actual, predicted):
    """Mean Absolute Percentage Error."""
    actual, predicted = np.array(actual), np.array(predicted)
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100


def mae(actual, predicted):
    """Mean Absolute Error."""
    return np.mean(np.abs(np.array(actual) - np.array(predicted)))


# ── Moving Average Forecast ───────────────────────────────────────────────────

def moving_average_forecast(series, window=3, steps=3):
    """
    Simple Moving Average — easy to explain in interviews.
    Returns forecasted values for next `steps` periods.
    """
    forecasts = []
    data = list(series)
    for _ in range(steps):
        avg = np.mean(data[-window:])
        forecasts.append(round(avg))
        data.append(avg)
    return forecasts


# ── ARIMA Forecast ────────────────────────────────────────────────────────────

def arima_forecast(series, steps=3, order=(1, 1, 1)):
    """
    ARIMA(p,d,q) forecast.
    Falls back to Moving Average if statsmodels is unavailable or series too short.
    """
    if not ARIMA_AVAILABLE or len(series) < 12:
        return moving_average_forecast(series, steps=steps)

    try:
        model = ARIMA(series, order=order)
        result = model.fit()
        forecast = result.forecast(steps=steps)
        return [max(0, int(v)) for v in forecast]
    except Exception:
        return moving_average_forecast(series, steps=steps)


# ── Per-Product Forecasting ───────────────────────────────────────────────────

def forecast_all_products(df, forecast_months=3):
    """
    For each product, fit ARIMA on historical monthly demand
    and forecast next `forecast_months` periods.

    Returns
    -------
    summary_df : DataFrame with MAPE, MAE, and next-period forecasts
    forecast_dict : dict  {product_id: [f1, f2, f3]}
    """
    results = []
    forecast_dict = {}

    products = df["product_id"].unique()

    for pid in products:
        pdata = (
            df[df["product_id"] == pid]
            .sort_values("date")
            .set_index("date")["units_sold"]
        )

        if len(pdata) < 6:
            continue

        # Train / test split (last 3 months = test)
        train = pdata.iloc[:-3]
        test  = pdata.iloc[-3:]
        pname = df[df["product_id"] == pid]["product_name"].iloc[0]

        # Fit on train, predict test period
        test_pred = arima_forecast(train.values, steps=3)

        # Evaluate
        mape_val = mape(test.values, test_pred)
        mae_val  = mae(test.values, test_pred)

        # Forecast future (fit on ALL data)
        future_forecast = arima_forecast(pdata.values, steps=forecast_months)
        forecast_dict[pid] = future_forecast

        results.append({
            "product_id":   pid,
            "product_name": pname,
            "MAPE_%":       round(mape_val, 2),
            "MAE_units":    round(mae_val, 1),
            f"forecast_m1": future_forecast[0],
            f"forecast_m2": future_forecast[1] if forecast_months > 1 else None,
            f"forecast_m3": future_forecast[2] if forecast_months > 2 else None,
        })

    summary_df = pd.DataFrame(results)
    return summary_df, forecast_dict


if __name__ == "__main__":
    from data.generate_data import generate_sales_data
    df = generate_sales_data()
    summary, fdict = forecast_all_products(df)
    print("\n📊 Demand Forecast Summary:")
    print(summary.to_string(index=False))
