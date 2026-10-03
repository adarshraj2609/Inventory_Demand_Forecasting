from typing import Iterable, Tuple

import numpy as np
import pandas as pd


def product_summary(
    df: pd.DataFrame,
    window: int = 7,
    overstock_multiplier: float = 2.0,
) -> pd.DataFrame:
    """Create a product-level demand and inventory summary."""
    latest_date = df["Date"].max()
    recent_start = latest_date - pd.Timedelta(days=window - 1)

    recent = df[df["Date"] >= recent_start]

    summary = (
        df.groupby(["Product_ID", "Product_Name", "Category"], as_index=False)
        .agg(
            Total_Units_Sold=("Units_Sold", "sum"),
            Average_Daily_Demand=("Units_Sold", "mean"),
            Current_Closing_Inventory=("Closing_Stock", "last"),
            Reorder_Level=("Reorder_Level", "last"),
            Unit_Price=("Unit_Price", "last"),
        )
    )

    recent_avg = (
        recent.groupby("Product_ID")["Units_Sold"]
        .mean()
        .rename("Recent_7_Day_Average")
        .reset_index()
    )

    recent14_start = latest_date - pd.Timedelta(days=13)
    recent14 = df[df["Date"] >= recent14_start]
    recent14_avg = (
        recent14.groupby("Product_ID")["Units_Sold"]
        .mean()
        .rename("Recent_14_Day_Average")
        .reset_index()
    )

    summary = summary.merge(recent_avg, on="Product_ID", how="left")
    summary = summary.merge(recent14_avg, on="Product_ID", how="left")

    summary["Forecast_Daily_Demand"] = summary["Recent_7_Day_Average"]
    summary["Forecast_7_Day_Demand"] = (
        summary["Forecast_Daily_Demand"] * 7
    )

    summary["Stock_Coverage_Days"] = np.where(
        summary["Forecast_Daily_Demand"] > 0,
        summary["Current_Closing_Inventory"] / summary["Forecast_Daily_Demand"],
        np.inf,
    )

    summary["Stock_Status"] = np.select(
        [
            summary["Current_Closing_Inventory"] < summary["Forecast_Daily_Demand"],
            summary["Current_Closing_Inventory"]
            > summary["Forecast_Daily_Demand"] * overstock_multiplier,
        ],
        ["Under-Stocked", "Potentially Over-Stocked"],
        default="Healthy",
    )

    summary["Monitoring_Priority"] = np.select(
        [
            summary["Stock_Status"] == "Under-Stocked",
            summary["Stock_Coverage_Days"] < 7,
            summary["Stock_Status"] == "Potentially Over-Stocked",
        ],
        ["High", "Medium", "Medium"],
        default="Normal",
    )

    return summary.sort_values(
        ["Monitoring_Priority", "Total_Units_Sold"], ascending=[True, False]
    ).reset_index(drop=True)


def monthly_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate demand by calendar month."""
    result = (
        df.assign(Month_Start=df["Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month_Start", as_index=False)
        .agg(Total_Units_Sold=("Units_Sold", "sum"))
    )
    return result


def weekday_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate demand by day of week in natural Monday-Sunday order."""
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    result = (
        df.groupby("Day_of_Week", as_index=False)
        .agg(Average_Units_Sold=("Units_Sold", "mean"))
    )
    result["Day_of_Week"] = pd.Categorical(
        result["Day_of_Week"], categories=order, ordered=True
    )
    return result.sort_values("Day_of_Week").reset_index(drop=True)


def product_trends(df: pd.DataFrame, window_days: int = 30) -> pd.DataFrame:
    """Compare recent demand with the first comparable period."""
    latest_date = df["Date"].max()
    early_end = df["Date"].min() + pd.Timedelta(days=window_days - 1)
    recent_start = latest_date - pd.Timedelta(days=window_days - 1)

    early = df[df["Date"] <= early_end]
    recent = df[df["Date"] >= recent_start]

    early_avg = (
        early.groupby("Product_ID")["Units_Sold"]
        .mean()
        .rename("Early_Average_Demand")
    )
    recent_avg = (
        recent.groupby("Product_ID")["Units_Sold"]
        .mean()
        .rename("Recent_Average_Demand")
    )

    result = pd.concat([early_avg, recent_avg], axis=1).reset_index()
    result["Demand_Change_Percent"] = np.where(
        result["Early_Average_Demand"] > 0,
        (result["Recent_Average_Demand"] - result["Early_Average_Demand"])
        / result["Early_Average_Demand"]
        * 100,
        np.nan,
    )
    result["Trend"] = np.select(
        [
            result["Demand_Change_Percent"] > 5,
            result["Demand_Change_Percent"] < -5,
        ],
        ["Increasing", "Decreasing"],
        default="Stable",
    )
    return result.sort_values("Demand_Change_Percent", ascending=False).reset_index(drop=True)


def forecast(df: pd.DataFrame, window: int = 7, horizon: int = 7) -> pd.DataFrame:
    """Create a simple future forecast using each product's latest N-day average."""
    latest_date = df["Date"].max()
    rows = []

    for product_id, group in df.groupby("Product_ID"):
        group = group.sort_values("Date")
        recent = group.tail(window)
        forecast_value = recent["Units_Sold"].mean()
        product_name = group["Product_Name"].iloc[-1]
        category = group["Category"].iloc[-1]
        current_stock = group["Closing_Stock"].iloc[-1]
        reorder_level = group["Reorder_Level"].iloc[-1]

        for day in range(1, horizon + 1):
            rows.append(
                {
                    "Date": latest_date + pd.Timedelta(days=day),
                    "Product_ID": product_id,
                    "Product_Name": product_name,
                    "Category": category,
                    "Forecast_Daily_Demand": forecast_value,
                    "Current_Closing_Inventory": current_stock,
                    "Reorder_Level": reorder_level,
                }
            )

    result = pd.DataFrame(rows)
    result["Cumulative_Forecast_Demand"] = result.groupby("Product_ID")[
        "Forecast_Daily_Demand"
    ].cumsum()
    result["Projected_Closing_Stock"] = (
        result["Current_Closing_Inventory"] - result["Cumulative_Forecast_Demand"]
    )
    result["Potential_Stockout"] = (
        result["Projected_Closing_Stock"] < 0
    )
    return result


def validate_forecast(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """Back-test the moving-average baseline where at least N prior observations exist."""
    data = df.sort_values(["Product_ID", "Date"]).copy()
    data["Forecast"] = data.groupby("Product_ID")["Units_Sold"].transform(
        lambda s: s.shift(1).rolling(window=window, min_periods=window).mean()
    )
    data = data.dropna(subset=["Forecast"])
    data["Absolute_Error"] = (data["Units_Sold"] - data["Forecast"]).abs()
    data["Squared_Error"] = (data["Units_Sold"] - data["Forecast"]) ** 2

    result = (
        data.groupby("Product_ID", as_index=False)
        .agg(
            MAE=("Absolute_Error", "mean"),
            MSE=("Squared_Error", "mean"),
            Observations=("Forecast", "count"),
        )
    )
    result["RMSE"] = np.sqrt(result["MSE"])
    return result.drop(columns=["MSE"])


def exponential_smoothing(values: Iterable[float], alpha: float = 0.30) -> np.ndarray:
    """Simple exponential smoothing implemented with NumPy only."""
    values = np.asarray(list(values), dtype=float)
    if values.size == 0:
        return np.array([])

    smoothed = np.empty(values.size, dtype=float)
    smoothed[0] = values[0]
    for i in range(1, values.size):
        smoothed[i] = alpha * values[i] + (1 - alpha) * smoothed[i - 1]
    return smoothed


def add_exponential_smoothing(df: pd.DataFrame, alpha: float = 0.30) -> pd.DataFrame:
    """Add product-level simple exponential smoothing values."""
    data = df.sort_values(["Product_ID", "Date"]).copy()
    data["Exponential_Smoothing"] = np.nan

    for product_id, group in data.groupby("Product_ID"):
        values = exponential_smoothing(group["Units_Sold"].tolist(), alpha)
        data.loc[group.index, "Exponential_Smoothing"] = values

    return data


def build_business_insights(
    df: pd.DataFrame,
    summary: pd.DataFrame,
    trends: pd.DataFrame,
    validation: pd.DataFrame,
) -> str:
    """Create a readable business-insights text report."""
    top_product = summary.sort_values("Total_Units_Sold", ascending=False).iloc[0]
    low_product = summary.sort_values("Total_Units_Sold", ascending=True).iloc[0]
    under = summary[summary["Stock_Status"] == "Under-Stocked"]
    over = summary[summary["Stock_Status"] == "Potentially Over-Stocked"]
    increasing = trends[trends["Trend"] == "Increasing"]
    decreasing = trends[trends["Trend"] == "Decreasing"]

    overall_mae = validation["MAE"].mean()
    overall_rmse = validation["RMSE"].mean()

    lines = [
        "INVENTORY DEMAND FORECASTING - BUSINESS INSIGHTS",
        "=" * 60,
        f"Analysis period: {df['Date'].min().date()} to {df['Date'].max().date()}",
        f"Products analyzed: {df['Product_ID'].nunique()}",
        f"Total units sold: {df['Units_Sold'].sum():,.0f}",
        "",
        "1. Demand leaders and laggards",
        f"- Highest total demand: {top_product['Product_Name']} ({top_product['Total_Units_Sold']:,.0f} units).",
        f"- Lowest total demand: {low_product['Product_Name']} ({low_product['Total_Units_Sold']:,.0f} units).",
        f"- Overall average daily demand: {df['Units_Sold'].mean():,.2f} units.",
        "",
        "2. Inventory position",
        f"- Under-stocked products: {len(under)}.",
        f"- Potentially over-stocked products: {len(over)}.",
        f"- Healthy stock position: {len(summary) - len(under) - len(over)}.",
        "",
        "3. Demand trend",
        f"- Increasing-demand products: {len(increasing)}.",
        f"- Decreasing-demand products: {len(decreasing)}.",
        f"- Stable-demand products: {len(summary) - len(increasing) - len(decreasing)}.",
        "",
        "4. Baseline forecast accuracy",
        f"- Mean product-level MAE: {overall_mae:,.2f} units.",
        f"- Mean product-level RMSE: {overall_rmse:,.2f} units.",
        "- The forecast is a 7-day moving-average baseline; accuracy should be interpreted as a simple benchmark rather than a production-grade model.",
        "",
        "5. Business interpretation",
        "- Under-stocked products deserve immediate monitoring because current stock is below the baseline daily forecast.",
        "- Potentially over-stocked products may tie up working capital and should be reviewed against actual replenishment policies.",
        "- Increasing-demand products may require closer reorder monitoring during the next planning cycle.",
        "- Weekly and monthly demand charts should be used to spot recurring seasonal patterns before changing stock policies.",
        "",
        "ASSUMPTION",
        "- Potentially over-stocked is defined as closing stock greater than 2x the 7-day average daily demand.",
    ]
    return "\n".join(lines)
