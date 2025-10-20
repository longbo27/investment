"""Performance metrics computation."""

from __future__ import annotations

import pandas as pd


def compute_summary(equity_curve: pd.Series) -> pd.DataFrame:
    """Return basic performance metrics from an equity curve."""
    returns = equity_curve.pct_change().dropna()
    cumulative = (1 + returns).prod() - 1
    annualised = (1 + cumulative) ** (252 / len(returns)) - 1 if not returns.empty else 0
    volatility = returns.std() * (252 ** 0.5)
    max_dd = (equity_curve / equity_curve.cummax() - 1).min()
    return pd.DataFrame(
        {
            "cumulative_return": [cumulative],
            "annualised_return": [annualised],
            "volatility": [volatility],
            "max_drawdown": [max_dd],
            "sharpe": [annualised / volatility if volatility else 0],
        }
    )
