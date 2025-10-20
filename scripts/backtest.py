"""Run a backtest using placeholder data."""

from __future__ import annotations

import pandas as pd

from src.backtest.engine import run_backtest
from src.core.utils import load_config


def main() -> None:
    cfg_model = load_config("model")
    cfg_risk = load_config("risk")
    prices = pd.read_parquet("data/processed/prices_sample.parquet")
    results = run_backtest(prices, cfg_model, cfg_risk)
    print(results["signals"].head())
    print(f"PNL proxy: {results['pnl_proxy']}")


if __name__ == "__main__":
    main()
