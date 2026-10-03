from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save_current_figure(output_path: Path, title: str) -> None:
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close()


def daily_sales_trend(df: pd.DataFrame, output_path: Path) -> None:
    daily = df.groupby("Date", as_index=False)["Units_Sold"].sum()
    plt.figure(figsize=(11, 5.5))
    plt.plot(daily["Date"], daily["Units_Sold"], linewidth=1.4)
    plt.xlabel("Date")
    plt.ylabel("Units Sold")
    _save_current_figure(output_path, "Daily Sales Trend")


def moving_average(
    df: pd.DataFrame,
    output_path: Path,
    windows=(3, 7, 14, 30),
) -> None:
    daily = df.groupby("Date", as_index=False)["Units_Sold"].sum()
    for window in windows:
        daily[f"MA_{window}"] = daily["Units_Sold"].rolling(window, min_periods=1).mean()

    plt.figure(figsize=(11, 5.5))
    plt.plot(daily["Date"], daily["Units_Sold"], linewidth=0.9, label="Actual")
    for window in windows:
        line_width = 1.2 if window == 7 else 1.0
        plt.plot(
            daily["Date"],
            daily[f"MA_{window}"],
            linewidth=line_width,
            label=f"{window}-Day MA",
        )
    plt.xlabel("Date")
    plt.ylabel("Units Sold")
    plt.legend()
    _save_current_figure(output_path, "Moving Average Analysis")


def top_products(df: pd.DataFrame, output_path: Path, top_n: int = 10) -> None:
    product_totals = (
        df.groupby("Product_Name", as_index=False)["Units_Sold"]
        .sum()
        .sort_values("Units_Sold", ascending=False)
        .head(top_n)
    )

    plt.figure(figsize=(10, 6))
    plt.barh(product_totals["Product_Name"], product_totals["Units_Sold"])
    plt.xlabel("Total Units Sold")
    plt.ylabel("Product")
    plt.gca().invert_yaxis()
    _save_current_figure(output_path, f"Top {top_n} Products by Demand")


def monthly_demand(monthly: pd.DataFrame, output_path: Path) -> None:
    plt.figure(figsize=(11, 5.5))
    plt.plot(
        monthly["Month_Start"],
        monthly["Total_Units_Sold"],
        marker="o",
        linewidth=1.4,
    )
    plt.xlabel("Month")
    plt.ylabel("Units Sold")
    _save_current_figure(output_path, "Monthly Demand")


def inventory_level(df: pd.DataFrame, output_path: Path) -> None:
    inventory = df.groupby("Date", as_index=False)["Closing_Stock"].sum()
    plt.figure(figsize=(11, 5.5))
    plt.plot(inventory["Date"], inventory["Closing_Stock"], linewidth=1.4)
    plt.xlabel("Date")
    plt.ylabel("Closing Inventory")
    _save_current_figure(output_path, "Inventory Level Trend")


def actual_vs_forecast(
    df: pd.DataFrame,
    output_path: Path,
    history_days: int = 120,
) -> None:
    daily = df.groupby("Date", as_index=False)["Units_Sold"].sum()
    daily["Forecast_7_Day"] = daily["Units_Sold"].shift(1).rolling(7, min_periods=7).mean()
    recent = daily.tail(history_days).dropna(subset=["Forecast_7_Day"])

    plt.figure(figsize=(11, 5.5))
    plt.plot(recent["Date"], recent["Units_Sold"], linewidth=1.1, label="Actual")
    plt.plot(recent["Date"], recent["Forecast_7_Day"], linewidth=1.2, label="7-Day Baseline Forecast")
    plt.xlabel("Date")
    plt.ylabel("Units Sold")
    plt.legend()
    _save_current_figure(output_path, "Actual vs Forecast")
