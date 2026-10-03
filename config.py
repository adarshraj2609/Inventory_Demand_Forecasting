from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RAW_DATA = BASE_DIR / "data" / "raw" / "inventory_sales.csv"
CLEAN_DATA = BASE_DIR / "data" / "processed" / "inventory_sales_cleaned.csv"

OUTPUT_DIR = BASE_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
RESULT_DIR = OUTPUT_DIR / "results"
LOG_DIR = BASE_DIR / "logs"

FORECAST_WINDOW = 7
FORECAST_HORIZON = 7
OVERSTOCK_MULTIPLIER = 2.0

ENABLE_EXPONENTIAL_SMOOTHING = True
SMOOTHING_ALPHA = 0.30

TOP_PRODUCT_COUNT = 10
TREND_WINDOW_DAYS = 30
MOVING_AVERAGE_WINDOWS = (3, 7, 14, 30)
FORECAST_CHART_HISTORY_DAYS = 120

DATE_COLUMN = "Date"
PRODUCT_COLUMN = "Product_ID"

REQUIRED_COLUMNS = [
    "Date",
    "Product_ID",
    "Sales",
    "Inventory"
]
