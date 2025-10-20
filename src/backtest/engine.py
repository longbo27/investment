"""Vectorised backtesting harness."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from ..core.portfolio import size_positions
from ..core.signal import generate_signals


def run_backtest(prices: pd.DataFrame, cfg_model: Dict, cfg_risk: Dict) -> Dict:
    """Simplified backtest that sizes positions and returns placeholder metrics."""
    signals = generate_signals(prices, cfg_model, cfg_risk)
    portfolio = size_positions(signals, equity=cfg_risk.get("starting_equity", 1000), cfg_risk=cfg_risk)
    pnl = (portfolio["shares"] * signals["expected_edge"].fillna(0)).sum()
    return {"signals": signals, "portfolio": portfolio, "pnl_proxy": pnl}
