import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

INPUT_FILE = "data/inventory_data.csv"

CLEAN_FILE = "output/cleaned_inventory_data.csv"

FORECAST_WINDOW = 7
FORECAST_HORIZON = 7
OVERSTOCK_MULTIPLIER = 1.20
TREND_WINDOW_DAYS = 7

TOP_PRODUCT_COUNT = 10

OUTPUT_FOLDER = "output"
CHART_FOLDER = "output/charts"


import os

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE)

print("Raw records:", len(df))
print("Columns:", list(df.columns))

print("\nCleaning data...")

# Convert Date column into datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Convert numeric columns
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
df["Inventory"] = pd.to_numeric(df["Inventory"], errors="coerce")

# Remove missing values
df = df.dropna(subset=[
    "Date",
    "Product_ID",
    "Sales",
    "Inventory"
])

# Remove negative sales
df = df[df["Sales"] >= 0]

# Remove negative inventory
df = df[df["Inventory"] >= 0]

# Sort data
df = df.sort_values(["Date", "Product_ID"])

# Reset index
df = df.reset_index(drop=True)

print("Cleaned records:", len(df))

# Save cleaned data
df.to_csv(CLEAN_FILE, index=False)

print("\n================ DATA INFORMATION ================")

print("Number of products:",
      df["Product_ID"].nunique())

print("Start date:",
      df["Date"].min().date())

print("End date:",
      df["Date"].max().date())

print("Total sales:",
      df["Sales"].sum())

print("Average daily sales:",
      df["Sales"].mean())

print("Average inventory:",
      df["Inventory"].mean())

product_summary = df.groupby("Product_ID").agg(
    Total_Sales=("Sales", "sum"),
    Average_Daily_Sales=("Sales", "mean"),
    Current_Inventory=("Inventory", "last"),
    Maximum_Sales=("Sales", "max"),
    Minimum_Sales=("Sales", "min")
).reset_index()


# Forecast demand for each product
forecast_values = []

for product in product_summary["Product_ID"]:

    product_data = df[df["Product_ID"] == product]

    recent_sales = product_data["Sales"].tail(
        FORECAST_WINDOW
    )

    forecast = recent_sales.mean()

    forecast_values.append(forecast)


product_summary["Forecast_Daily_Demand"] = forecast_values

# Forecast for next 7 days
product_summary["Forecast_7_Day_Demand"] = (
    product_summary["Forecast_Daily_Demand"]
    * FORECAST_HORIZON
)

# Required stock
product_summary["Required_Stock"] = (
    product_summary["Forecast_7_Day_Demand"]
    * OVERSTOCK_MULTIPLIER
)

# Stock difference
product_summary["Stock_Difference"] = (
    product_summary["Current_Inventory"]
    - product_summary["Required_Stock"]
)


# Stock status
def stock_status(row):

    if row["Current_Inventory"] < row["Forecast_7_Day_Demand"]:
        return "UNDERSTOCK"

    elif row["Current_Inventory"] > row["Required_Stock"]:
        return "OVERSTOCK"

    else:
        return "NORMAL"


product_summary["Stock_Status"] = (
    product_summary.apply(stock_status, axis=1)
)


# Sort by sales
product_summary = product_summary.sort_values(
    "Total_Sales",
    ascending=False
)

product_summary.to_csv(
    f"{OUTPUT_FOLDER}/product_summary.csv",
    index=False
)

daily_sales = df.groupby("Date")["Sales"].sum().reset_index()

daily_sales = daily_sales.sort_values("Date")

daily_sales["Moving_Average_3"] = (
    daily_sales["Sales"]
    .rolling(window=3)
    .mean()
)

daily_sales["Moving_Average_7"] = (
    daily_sales["Sales"]
    .rolling(window=7)
    .mean()
)

daily_sales["Moving_Average_14"] = (
    daily_sales["Sales"]
    .rolling(window=14)
    .mean()
)


daily_sales.to_csv(
    f"{OUTPUT_FOLDER}/daily_sales_analysis.csv",
    index=False
)

last_7_days = daily_sales["Sales"].tail(
    FORECAST_WINDOW
)

daily_forecast = last_7_days.mean()

future_dates = pd.date_range(
    start=daily_sales["Date"].max()
    + pd.Timedelta(days=1),

    periods=FORECAST_HORIZON,

    freq="D"
)

future_forecast = pd.DataFrame({
    "Date": future_dates,
    "Forecast_Demand": np.repeat(
        daily_forecast,
        FORECAST_HORIZON
    )
})


future_forecast.to_csv(
    f"{OUTPUT_FOLDER}/demand_forecast.csv",
    index=False
)


df["Month"] = df["Date"].dt.to_period("M").astype(str)

monthly_demand = (
    df.groupby("Month")["Sales"]
    .sum()
    .reset_index()
)

monthly_demand.to_csv(
    f"{OUTPUT_FOLDER}/monthly_demand.csv",
    index=False
)


df["Weekday"] = df["Date"].dt.day_name()

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday_demand = (
    df.groupby("Weekday")["Sales"]
    .mean()
    .reindex(weekday_order)
    .reset_index()
)

weekday_demand.rename(
    columns={
        "Sales": "Average_Demand"
    },
    inplace=True
)

weekday_demand.to_csv(
    f"{OUTPUT_FOLDER}/weekday_demand.csv",
    index=False
)



trend_results = []

for product in df["Product_ID"].unique():

    product_data = df[
        df["Product_ID"] == product
    ].sort_values("Date")

    if len(product_data) >= TREND_WINDOW_DAYS * 2:

        recent = product_data["Sales"].tail(
            TREND_WINDOW_DAYS
        ).mean()

        previous = product_data["Sales"].iloc[
            -TREND_WINDOW_DAYS * 2:
            -TREND_WINDOW_DAYS
        ].mean()

        if previous != 0:

            change_percentage = (
                (recent - previous)
                / previous
            ) * 100

        else:

            change_percentage = 0

        if change_percentage > 5:

            trend = "INCREASING"

        elif change_percentage < -5:

            trend = "DECREASING"

        else:

            trend = "STABLE"

        trend_results.append([
            product,
            recent,
            previous,
            change_percentage,
            trend
        ])


product_trends = pd.DataFrame(
    trend_results,
    columns=[
        "Product_ID",
        "Recent_Average",
        "Previous_Average",
        "Change_Percentage",
        "Trend"
    ]
)

product_trends.to_csv(
    f"{OUTPUT_FOLDER}/product_trends.csv",
    index=False
)


validation_results = []

for product in df["Product_ID"].unique():

    product_data = df[
        df["Product_ID"] == product
    ].sort_values("Date")

    if len(product_data) > FORECAST_WINDOW + 1:

        actual = product_data["Sales"].iloc[-1]

        previous_data = product_data["Sales"].iloc[
            -FORECAST_WINDOW - 1:
            -1
        ]

        predicted = previous_data.mean()

        error = abs(actual - predicted)

        if actual != 0:

            percentage_error = (
                error / actual
            ) * 100

        else:

            percentage_error = 0

        validation_results.append([
            product,
            actual,
            predicted,
            error,
            percentage_error
        ])


validation = pd.DataFrame(
    validation_results,
    columns=[
        "Product_ID",
        "Actual",
        "Predicted",
        "Absolute_Error",
        "Percentage_Error"
    ]
)

validation.to_csv(
    f"{OUTPUT_FOLDER}/forecast_validation.csv",
    index=False
)


print("\n================ BUSINESS INSIGHTS ================")

highest_sales_product = (
    product_summary.iloc[0]["Product_ID"]
)

highest_sales_value = (
    product_summary.iloc[0]["Total_Sales"]
)

print(
    "Top selling product:",
    highest_sales_product
)

print(
    "Top product sales:",
    highest_sales_value
)


# Understock products
understock_products = product_summary[
    product_summary["Stock_Status"]
    == "UNDERSTOCK"
]

# Overstock products
overstock_products = product_summary[
    product_summary["Stock_Status"]
    == "OVERSTOCK"
]


print(
    "Understock products:",
    len(understock_products)
)

print(
    "Overstock products:",
    len(overstock_products)
)


plt.figure(figsize=(12, 6))

plt.plot(
    daily_sales["Date"],
    daily_sales["Sales"]
)

plt.title("Daily Sales Trend")

plt.xlabel("Date")

plt.ylabel("Sales")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{CHART_FOLDER}/01_daily_sales_trend.png"
)

plt.close()


plt.figure(figsize=(12, 6))

plt.plot(
    daily_sales["Date"],
    daily_sales["Sales"],
    label="Actual Sales"
)

plt.plot(
    daily_sales["Date"],
    daily_sales["Moving_Average_7"],
    label="7-Day Moving Average"
)

plt.plot(
    daily_sales["Date"],
    daily_sales["Moving_Average_14"],
    label="14-Day Moving Average"
)

plt.title("Sales and Moving Average")

plt.xlabel("Date")

plt.ylabel("Sales")

plt.legend()

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{CHART_FOLDER}/02_moving_average.png"
)

plt.close()


top_products = product_summary.head(
    TOP_PRODUCT_COUNT
)

plt.figure(figsize=(12, 6))

plt.bar(
    top_products["Product_ID"].astype(str),
    top_products["Total_Sales"]
)

plt.title("Top Products by Sales")

plt.xlabel("Product")

plt.ylabel("Total Sales")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{CHART_FOLDER}/03_top_products.png"
)

plt.close()



plt.figure(figsize=(12, 6))

plt.plot(
    monthly_demand["Month"],
    monthly_demand["Sales"],
    marker="o"
)

plt.title("Monthly Demand")

plt.xlabel("Month")

plt.ylabel("Total Demand")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{CHART_FOLDER}/04_monthly_demand.png"
)

plt.close()


daily_inventory = (
    df.groupby("Date")["Inventory"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(12, 6))

plt.plot(
    daily_inventory["Date"],
    daily_inventory["Inventory"]
)

plt.title("Average Inventory Level")

plt.xlabel("Date")

plt.ylabel("Inventory")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{CHART_FOLDER}/05_inventory_level.png"
)

plt.close()


history = daily_sales.tail(
    FORECAST_CHART_DAYS := 30
)

plt.figure(figsize=(12, 6))

plt.plot(
    history["Date"],
    history["Sales"],
    label="Actual Demand"
)

plt.plot(
    future_forecast["Date"],
    future_forecast["Forecast_Demand"],
    linestyle="--",
    label="Forecast Demand"
)

plt.title("Actual vs Forecast Demand")

plt.xlabel("Date")

plt.ylabel("Demand")

plt.legend()

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{CHART_FOLDER}/06_actual_vs_forecast.png"
)

plt.close()


summary = {
    "Raw Records": len(pd.read_csv(INPUT_FILE)),
    "Cleaned Records": len(df),
    "Number of Products": df["Product_ID"].nunique(),
    "Start Date": str(df["Date"].min().date()),
    "End Date": str(df["Date"].max().date()),
    "Total Sales": float(df["Sales"].sum()),
    "Average Daily Sales": float(df["Sales"].mean()),
    "Forecast Window": FORECAST_WINDOW,
    "Forecast Horizon": FORECAST_HORIZON,
    "Understock Products": len(understock_products),
    "Overstock Products": len(overstock_products)
}


summary_df = pd.DataFrame(
    [summary]
)

summary_df.to_csv(
    f"{OUTPUT_FOLDER}/project_summary.csv",
    index=False
)


print("\n================================================")
print("INVENTORY DEMAND FORECASTING COMPLETED")
print("================================================")

print("Cleaned data:")
print(CLEAN_FILE)

print("\nResults:")
print(OUTPUT_FOLDER)

print("\nCharts:")
print(CHART_FOLDER)

print("\nForecasted daily demand:",
      round(daily_forecast, 2))

print("\nPipeline completed successfully!")
