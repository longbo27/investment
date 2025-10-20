"""Data loading and preprocessing utilities."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd

from .utils import ensure_columns


@dataclass
class DataRequest:
    symbols: Iterable[str]
    start: dt.date
    end: Optional[dt.date] = None
    frequency: str = "D"


def load_local_prices(path: str, symbols: Iterable[str]) -> pd.DataFrame:
    """Load cached prices from a parquet/CSV file (placeholder)."""
    _ = path, symbols  # suppress unused variable warnings
    raise NotImplementedError("Implement local price loading for your data source")


def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise OHLCV columns and forward-fill missing values."""
    ensure_columns(df, ["open", "high", "low", "close", "volume"])
    df = df.sort_index().copy()
    df = df.ffill()
    return df
