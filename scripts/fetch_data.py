"""Fetch and cache market data for the configured universe."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.core.utils import load_config


def main() -> None:
    cfg_data = load_config("data")
    cfg_universe = load_config("universe")
    symbols = [entry["symbol"] for entry in cfg_universe["etfs"]]

    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    cash_series = 100 + np.cumsum(np.random.normal(0, 0.2, size=len(dates)))

    frames = []
    for symbol in symbols:
        prices = np.cumsum(np.random.normal(0, 1, size=len(dates))) + 100
        df = pd.DataFrame(
            {
                "open": prices + np.random.normal(0, 0.5, size=len(dates)),
                "high": prices + np.abs(np.random.normal(0, 1, size=len(dates))),
                "low": prices - np.abs(np.random.normal(0, 1, size=len(dates))),
                "close": prices,
                "volume": np.random.randint(1_000_000, 2_000_000, size=len(dates)),
                "cash_proxy": cash_series,
                "symbol": symbol,
            },
            index=dates,
        )
        frames.append(df)

    panel = pd.concat(frames)
    panel.index.name = "date"
    panel = panel.set_index("symbol", append=True)
    panel.to_parquet("data/processed/prices_sample.parquet")
    print(f"Saved synthetic data for symbols: {symbols}")
    _ = cfg_data


if __name__ == "__main__":
    main()
