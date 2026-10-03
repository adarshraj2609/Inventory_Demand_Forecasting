# Inventory Demand Forecasting Using Python, Pandas and Matplotlib

An industry-style, modular Python project for analyzing historical product demand, calculating moving averages, generating a simple 7-day baseline forecast, comparing demand with inventory, and identifying products that require closer stock monitoring.

## Technology Stack

- Python
- Pandas
- NumPy
- Matplotlib
- VS Code

No Jupyter Notebook, Google Colab, scikit-learn, statsmodels, Power BI, Streamlit, or other framework is required.

## Project Structure

```text
Inventory_Demand_Forecasting/
├── main.py
├── config.py
├── data/
│   ├── data_dictionary.csv
│   │   
│   └── inventory_data.csv
│       
├── outputs/
│   ├── charts/
│   └── results/
├── requirements.txt
├── PROJECT_REPORT.md
└── STEP_BY_STEP.md
```

## Important Dataset Note

The included dataset is **synthetic demonstration data** created for this academic/project implementation. It follows the required business schema and includes daily product sales, stock, reorder levels, prices, weekend patterns, and seasonal variation. It should not be presented as real company data.

## Core Business Logic

### 1. Cleaning
- Converts `Date` into a date/time field.
- Converts numeric fields to numeric data types.
- Removes duplicate records.
- Removes invalid negative sales/stock records.
- Sorts each product chronologically.

### 2. Moving Average
The project calculates 3-day, 7-day, 14-day, and 30-day moving averages.

The required baseline forecast is:

```text
Forecast Demand = Average demand of previous 7 days
```

### 3. Inventory Classification

The project uses this documented assumption:

```text
Closing Stock < Forecast Daily Demand
    -> Under-Stocked

Closing Stock > 2 × Forecast Daily Demand
    -> Potentially Over-Stocked

Otherwise
    -> Healthy
```

The `2x` over-stock threshold is an assumption and should be reviewed for a real business.

### 4. Forecast Validation

A historical back-test calculates:

- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)

These metrics evaluate the simple 7-day moving-average baseline where enough historical observations exist.

### 5. Optional Exponential Smoothing

A simple exponential smoothing series is implemented manually with NumPy. It is enabled in `config.py` and does not require `statsmodels`.

## Outputs

After `python main.py`, the project creates:

### Charts

- `01_daily_sales_trend.png`
- `02_moving_average.png`
- `03_top_products.png`
- `04_monthly_demand.png`
- `05_inventory_level.png`
- `06_actual_vs_forecast.png`

### Result tables

- `cleanned_inventory_data.csv`
- `demand_forecast.csv`
- `monthly_demand.csv`
- `weekday_demand.csv`
- `product_trends.csv`
- `forecast_validation.csv`
- `project_summary.csv`
- `daily_sales_analysis`
- 

## Configuration

All major project assumptions are kept in `config.py`, including the forecast window, forecast horizon, over-stock multiplier, and exponential smoothing setting. This avoids scattering hard-coded business values across the codebase.

## Run

```bash
python -m venv .venv
```

Windows Command Prompt:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Business Questions Answered

The generated result files support analysis of:

1. Highest-demand products.
2. Lowest-demand products.
3. Average daily demand.
4. Meaning and impact of a 7-day moving average.
5. Weekly and monthly demand patterns.
6. Increasing-demand products.
7. Decreasing-demand products.
8. Under-stocked products.
9. Potentially over-stocked products.
10. Products that require closer monitoring.
11. Baseline forecast accuracy using MAE and RMSE.
# Inventory_Forecast
