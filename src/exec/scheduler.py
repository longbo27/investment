"""Job scheduler entrypoints for daily/weekly execution."""

from __future__ import annotations

import logging
from typing import Callable, Dict

LOGGER = logging.getLogger(__name__)


def run_with_retry(job: Callable[[], None], cfg: Dict) -> None:
    """Execute a job with retry semantics based on configuration."""
    attempts = 0
    max_attempts = cfg.get("retry", {}).get("max_attempts", 3)
    while attempts < max_attempts:
        try:
            job()
            return
        except Exception as exc:  # noqa: BLE001 - top-level retry handler
            attempts += 1
            LOGGER.exception("Job failed on attempt %s/%s", attempts, max_attempts)
            if attempts >= max_attempts:
                raise
