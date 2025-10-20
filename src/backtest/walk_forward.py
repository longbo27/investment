"""Walk-forward validation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import pandas as pd

from ..core.model import save_model, train_model


@dataclass
class WalkForwardWindow:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_end: pd.Timestamp


def generate_windows(index: Iterable[pd.Timestamp], cfg: Dict) -> List[WalkForwardWindow]:
    """Yield rolling windows based on configuration."""
    index = pd.DatetimeIndex(index)
    windows = []
    train_days = cfg["walk_forward"]["window_train_days"]
    test_days = cfg["walk_forward"]["window_test_days"]
    step_days = cfg["walk_forward"]["step_days"]
    start = index.min()
    while start + pd.Timedelta(days=train_days + test_days) <= index.max():
        train_end = start + pd.Timedelta(days=train_days)
        test_end = train_end + pd.Timedelta(days=test_days)
        windows.append(WalkForwardWindow(start, train_end, test_end))
        start += pd.Timedelta(days=step_days)
    return windows


def walk_forward_train(prices: pd.DataFrame, cfg_model: Dict, cfg_backtest: Dict) -> None:
    """Train models sequentially and persist the latest."""
    windows = generate_windows(prices.index, cfg_backtest)
    for window in windows:
        subset = prices.loc[window.train_start : window.train_end]
        model, metadata = train_model(subset, cfg_model)
        save_model(model, metadata)
