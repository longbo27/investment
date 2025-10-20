"""Centralised logging configuration."""

from __future__ import annotations

import logging
from logging import Logger

from loguru import logger as loguru_logger


def configure_logging(level: str = "INFO") -> Logger:
    """Configure both stdlib logging and loguru for consistent output."""
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))
    loguru_logger.remove()
    loguru_logger.add(lambda msg: logging.getLogger("quant-ai-1k").log(logging.INFO, msg))
    return logging.getLogger("quant-ai-1k")
