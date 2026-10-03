from pathlib import Path
import pandas as pd

from config import REQUIRED_COLUMNS


def load_inventory_data(file_path: Path) -> pd.DataFrame:
    """Load the raw inventory and sales CSV after validating its schema."""
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: " + ", ".join(missing_columns)
        )

    return df
