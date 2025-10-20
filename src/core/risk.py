"""Risk management primitives for order sizing and guardrails."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd


def position_size(equity: float, atr: float, price: float, cfg_risk: Dict) -> int:
    """ATR-based position sizing respecting per-trade risk."""
    stop_dist = cfg_risk.get("stop_atr_mult", 2.0) * atr
    if stop_dist <= 0 or price <= 0:
        return 0
    risk_cap = cfg_risk.get("risk_per_trade", 0.03) * equity
    shares = int(risk_cap / stop_dist)
    per_asset_cap = cfg_risk.get("position_max_per_asset", 0.2) * equity / price
    return max(0, min(shares, int(per_asset_cap)))


@dataclass
class RiskState:
    equity: float
    peak_equity: float
    drawdown: float = 0.0
    cooldown_days_remaining: int = 0
    daily_pnl: float = 0.0
    trades_today: List[Dict] = field(default_factory=list)


class RiskManager:
    """Stateful risk checks across drawdowns, exposure, and cooldowns."""

    def __init__(self, state: RiskState, cfg: Dict):
        self.state = state
        self.cfg = cfg

    def update_equity(self, equity: float) -> None:
        self.state.equity = equity
        self.state.peak_equity = max(self.state.peak_equity, equity)
        self.state.drawdown = (equity / self.state.peak_equity) - 1

    def check_drawdown(self) -> str:
        if self.state.drawdown <= self.cfg.get("max_drawdown_hard", -0.5):
            return "hard_stop"
        if self.state.drawdown <= self.cfg.get("max_drawdown_soft", -0.25):
            return "soft_stop"
        return "ok"

    def register_trade(self, trade: Dict) -> None:
        self.state.trades_today.append(trade)
        self.state.daily_pnl += trade.get("pnl", 0.0)

    def can_trade(self) -> bool:
        if self.state.cooldown_days_remaining > 0:
            return False
        if self.state.daily_pnl <= self.cfg.get("daily_loss_limit", -0.05) * self.state.equity:
            self.state.cooldown_days_remaining = self.cfg.get("cooldown_days_after_hit", 3)
            return False
        if self.check_drawdown() == "hard_stop":
            self.state.cooldown_days_remaining = self.cfg.get("cooldown_days_after_hit", 3)
            return False
        return True

    def filter_orders(self, proposed: pd.DataFrame) -> pd.DataFrame:
        if proposed.empty or not self.can_trade():
            return proposed.iloc[0:0]
        gross_exposure = (proposed["shares"] * proposed["price"]).sum() / self.state.equity
        if gross_exposure > self.cfg.get("position_max_gross", 1.0):
            scale = self.cfg.get("position_max_gross", 1.0) / gross_exposure
            proposed["shares"] = (proposed["shares"] * scale).astype(int)
        per_asset_cap = self.cfg.get("position_max_per_asset", 0.2)
        proposed["max_shares"] = (
            per_asset_cap * self.state.equity / proposed["price"]
        ).astype(int)
        proposed["shares"] = proposed[["shares", "max_shares"]].min(axis=1)
        return proposed.drop(columns=["max_shares"])
