"""Train the ML model on cached data."""

from __future__ import annotations

import pandas as pd

from src.core.model import save_model, train_model
from src.core.utils import load_config


def main() -> None:
    cfg_model = load_config("model")
    prices = pd.read_parquet("data/processed/prices_sample.parquet")
    model, metadata = train_model(prices, cfg_model)
    save_model(model, metadata)
    print("Model trained and saved.")


if __name__ == "__main__":
    main()
