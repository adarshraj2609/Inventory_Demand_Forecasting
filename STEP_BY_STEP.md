# Step-by-Step Execution Guide

## Step 1: Open the project

Extract the project ZIP and open the `Inventory_Demand_Forecasting` folder in VS Code.

## Step 2: Check Python

Open the VS Code terminal and run:

```bash
python --version
```

Python 3.10+ is recommended.

## Step 3: Create a virtual environment

```bash
python -m venv .venv
```

## Step 4: Activate the environment

### Windows CMD

```bat
.venv\Scripts\activate
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

## Step 5: Install the required libraries

```bash
pip install -r requirements.txt
```

Only the required stack is installed: Pandas, NumPy, and Matplotlib.

## Step 6: Confirm the dataset

The raw dataset is already present at:

```text
data/raw/inventory_sales.csv
```

The columns are:

```text
Date
Product_ID
Sales
Inventory

## Step 7: Run the complete project

```bash
python main.py
```

The terminal will show the pipeline progress.

## Step 8: Check processed data

Open:

```text
data/processed/inventory_sales_cleaned.csv
```

This contains cleaned records and derived fields such as sales value, month, weekday, and moving averages.

## Step 9: Check the charts

Open:

```text
outputs/charts/
```

Six PNG charts are created for demand, moving averages, products, monthly demand, inventory, and actual-versus-forecast analysis.

## Step 10: Check the result tables

Open:

```text
outputs/results/
```

Most important files:

- `product_summary.csv` - product-level business summary.
- `demand_forecast.csv` - next 7 days of baseline forecast.
- `forecast_validation.csv` - MAE and RMSE by product.
- `product_trends.csv` - increasing/decreasing/stable demand.
- `business_insights.txt` - readable findings.

## Step 11: Modify business assumptions

Open:

```text
config.py
```

Change values such as:

```python
FORECAST_WINDOW = 7
FORECAST_HORIZON = 7
OVERSTOCK_MULTIPLIER = 2.0
SMOOTHING_ALPHA = 0.30
```

Then rerun:

```bash
python main.py
```

## Step 12: GitHub

Do not add virtual-environment folders or runtime logs. The provided `.gitignore` already excludes common local Python files and log output.

The CSV dataset may be committed because it is synthetic demonstration data.
