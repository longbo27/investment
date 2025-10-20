"""Alerting helpers for email/Telegram notifications."""

from __future__ import annotations

from typing import Dict


def send_alert(message: str, cfg: Dict) -> None:
    """Placeholder alert dispatcher."""
    _ = message, cfg
    raise NotImplementedError("Integrate with your notification channels")
