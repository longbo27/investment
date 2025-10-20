"""Cost modelling for commissions, slippage, and FX."""

from __future__ import annotations

from typing import Dict

import pandas as pd


def estimate_costs(df: pd.DataFrame, cfg_risk: Dict) -> pd.Series:
    """Very rough cost model combining slippage and commissions."""
    commission = cfg_risk.get("commission_per_share", 0.01)
    slippage_bps = cfg_risk.get("slippage_bps", 10)
    price = df.groupby(level="symbol")["close"].transform(lambda s: s.ffill())
    per_share_slippage = price * slippage_bps / 10000
    return commission + per_share_slippage
