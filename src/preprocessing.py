import numpy as np
import pandas as pd

from config import MOVING_AVERAGE_WINDOWS


def clean_inventory_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw inventory data and create time-series helper columns."""
    data = df.copy()

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    numeric_columns = [
        "Units_Sold",
        "Opening_Stock",
        "Closing_Stock",
        "Reorder_Level",
        "Unit_Price",
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.drop_duplicates()
    data = data.dropna(subset=["Date", "Product_ID", "Product_Name", "Units_Sold"])

    # Negative sales and negative stock are treated as invalid records.
    for column in ["Units_Sold", "Opening_Stock", "Closing_Stock", "Reorder_Level", "Unit_Price"]:
        data = data[data[column].isna() | (data[column] >= 0)]

    data["Units_Sold"] = data["Units_Sold"].fillna(0)
    data["Opening_Stock"] = data["Opening_Stock"].fillna(0)
    data["Closing_Stock"] = data["Closing_Stock"].fillna(0)
    data["Reorder_Level"] = data["Reorder_Level"].fillna(0)
    data["Unit_Price"] = data["Unit_Price"].fillna(0)

    data = data.sort_values(["Product_ID", "Date"]).reset_index(drop=True)

    data["Sales_Value"] = data["Units_Sold"] * data["Unit_Price"]
    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.month
    data["Month_Name"] = data["Date"].dt.strftime("%b")
    data["Day_of_Week"] = data["Date"].dt.day_name()
    data["Day_Number"] = data["Date"].dt.dayofweek
    data["Week"] = data["Date"].dt.to_period("W").astype(str)

    grouped = data.groupby("Product_ID", group_keys=False)
    for window in MOVING_AVERAGE_WINDOWS:
        data[f"Moving_Average_{window}"] = grouped["Units_Sold"].transform(
            lambda series: series.rolling(window=window, min_periods=1).mean()
        )

    # Inventory consistency check: closing stock should not be negative.
    data["Stock_Status_Check"] = np.where(
        data["Closing_Stock"] < 0, "Invalid", "Valid"
    )

    return data
