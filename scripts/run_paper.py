"""Execute the paper trading loop."""

from __future__ import annotations

import pandas as pd

from src.core.portfolio import size_positions
from src.core.signal import generate_signals
from src.core.utils import load_config


def main() -> None:
    cfg_model = load_config("model")
    cfg_risk = load_config("risk")
    prices = pd.read_parquet("data/processed/prices_sample.parquet")
    signals = generate_signals(prices, cfg_model, cfg_risk)
    portfolio = size_positions(signals, equity=cfg_risk.get("starting_equity", 1000), cfg_risk=cfg_risk)
    print(portfolio.head())


if __name__ == "__main__":
    main()
