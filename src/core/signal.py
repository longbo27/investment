"""Signal generation combining rule-based filters with AI probability scores."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from .costs import estimate_costs
from .features import build_features
from .model import infer_proba, load_model


def rule_filter(features: pd.DataFrame) -> pd.Series:
    """Basic trend and volatility filters."""
    trend_ok = features["trend_100_over_200"] > 0
    atr_mean = features.groupby(level="symbol")["atr_14"].transform(lambda s: s.rolling(20).mean())
    volatility = features.groupby(level="symbol")["close"].transform(
        lambda s: s.pct_change().rolling(20).std() * (252 ** 0.5)
    )
    atr_ok = atr_mean < volatility
    return trend_ok & atr_ok.fillna(False)


def generate_signals(prices: pd.DataFrame, cfg_model: Dict, cfg_risk: Dict) -> pd.DataFrame:
    """Create candidate signals with probability scores."""
    features = build_features(prices)
    if features.empty:
        return pd.DataFrame(columns=["prob", "expected_edge", "close"])

    pass_mask = rule_filter(features)
    candidates = features.loc[pass_mask].copy()

    if candidates.empty:
        return pd.DataFrame(columns=["prob", "expected_edge", "close"])

    candidates["est_cost"] = estimate_costs(candidates, cfg_risk)
    candidates = candidates[candidates["est_cost"] > 0]
    if candidates.empty:
        return pd.DataFrame(columns=["prob", "expected_edge", "close"])

    model_bundle = load_model()
    proba = infer_proba(model_bundle, candidates)
    threshold = cfg_model.get("threshold", 0.6)
    pass_idx = proba >= threshold
    signals = candidates.loc[pass_idx].copy()
    signals["prob"] = proba.loc[pass_idx]
    signals["expected_edge"] = signals["prob"] - 0.5
    return signals
