"""Main live trading loop (placeholder)."""

from __future__ import annotations

import pandas as pd

from src.core.portfolio import size_positions
from src.core.risk import RiskManager, RiskState
from src.core.signal import generate_signals
from src.core.utils import load_config
from src.exec.broker_ibkr import IBKRClient
from src.monitor.logger import configure_logging


def main() -> None:
    logger = configure_logging()
    cfg_model = load_config("model")
    cfg_risk = load_config("risk")
    cfg_execution = load_config("execution")

    broker = IBKRClient(cfg_execution)
    logger.info("Connect broker (placeholder)")

    prices = pd.read_parquet("data/processed/prices_sample.parquet")
    signals = generate_signals(prices, cfg_model, cfg_risk)
    equity = cfg_risk.get("starting_equity", 1000)
    state = RiskState(equity=equity, peak_equity=equity)
    risk_manager = RiskManager(state, cfg_risk)
    orders = size_positions(signals, equity, cfg_risk)
    filtered_orders = risk_manager.filter_orders(orders)
    logger.info("Orders ready: %s", filtered_orders.to_dict("records"))
    logger.info("Integrate broker order placement before going live.")


if __name__ == "__main__":
    main()
