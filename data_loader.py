"""
data_loader.py
Load and clean airport/city data from Excel or CSV.
"""

from pathlib import Path
from typing import Optional

import pandas as pd


# Default path to airport data (Excel or CSV)
DATA_DIR = Path(__file__).resolve().parent / "data"
EXCEL_PATH = DATA_DIR / "airport_data.xlsx"
CSV_PATH = DATA_DIR / "airport_data.csv"

REQUIRED_COLUMNS = [
    "City",
    "Country",
    "Latitude",
    "Longitude",
    "Distance to Doha",
    "Distance to Dubai",
    "Distance to Abu Dhabi",
]


def load_airport_data(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load airport/city data from Excel or CSV.
    Tries Excel first; falls back to CSV if Excel missing or openpyxl unavailable.

    Returns:
        DataFrame with columns: City, Country, Latitude, Longitude,
        Distance to Doha, Distance to Dubai, Distance to Abu Dhabi.

    Raises:
        FileNotFoundError: If neither Excel nor CSV exists.
        ValueError: If required columns are missing or data is invalid.
    """
    path = path or EXCEL_PATH
    df: Optional[pd.DataFrame] = None

    if path.suffix.lower() == ".xlsx" and path.exists():
        try:
            df = pd.read_excel(path, sheet_name=0)
        except Exception:
            pass
    elif path.suffix.lower() == ".csv" and path.exists():
        df = pd.read_csv(path)

    if df is None:
        # Try known paths
        if EXCEL_PATH.exists():
            try:
                df = pd.read_excel(EXCEL_PATH, sheet_name=0)
            except Exception:
                df = None
        if df is None and CSV_PATH.exists():
            df = pd.read_csv(CSV_PATH)
        if df is None:
            raise FileNotFoundError(
                f"Airport data not found. Place airport_data.xlsx or airport_data.csv in {DATA_DIR}"
            )

    return clean_airport_data(df)


def clean_airport_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate airport data.
    - Strip column names
    - Ensure required columns exist
    - Drop rows with missing essential values
    - Normalize numeric columns
    """
    df = df.copy()
    df.columns = df.columns.str.strip()

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[REQUIRED_COLUMNS].copy()
    df["City"] = df["City"].astype(str).str.strip()
    df["Country"] = df["Country"].astype(str).str.strip()

    for col in ["Latitude", "Longitude", "Distance to Doha", "Distance to Dubai", "Distance to Abu Dhabi"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["City", "Latitude", "Longitude"])
    df = df.drop_duplicates(subset=["City", "Country"], keep="first").reset_index(drop=True)

    return df
