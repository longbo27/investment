"""Portfolio sizing and rebalancing utilities."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from .risk import position_size


def size_positions(signals: pd.DataFrame, equity: float, cfg_risk: Dict) -> pd.DataFrame:
    """Attach share counts to signals based on ATR risk sizing."""
    if signals.empty:
        return signals
    signals = signals.copy()
    signals["shares"] = [
        position_size(equity, row.get("atr_14", 0.0), row.get("close", 0.0), cfg_risk)
        for _, row in signals.iterrows()
    ]
    signals["price"] = signals["close"]
    signals = signals[signals["shares"] > 0]
    return signals


def rebalance(current: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    """Placeholder rebalance logic comparing current vs target positions."""
    _ = current, target
    raise NotImplementedError("Implement broker-specific rebalance logic")
