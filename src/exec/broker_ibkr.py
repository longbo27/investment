"""IBKR broker adapter using ib_insync (placeholder)."""

from __future__ import annotations

from typing import Dict, List


class IBKRClient:
    """Minimal interface for order placement and account queries."""

    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.paper = cfg.get("paper", True)

    def connect(self) -> None:
        """Connect to IBKR TWS/Gateway (implement with ib_insync)."""
        raise NotImplementedError("Implement IBKR connection using ib_insync")

    def account_equity(self) -> float:
        """Return current account equity."""
        raise NotImplementedError

    def place_orders(self, orders: List[Dict]) -> List[Dict]:
        """Submit a batch of orders and return execution reports."""
        raise NotImplementedError

    def reconcile(self) -> None:
        """Fetch fills and update local state/logs."""
        raise NotImplementedError
