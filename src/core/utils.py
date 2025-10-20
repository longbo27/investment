"""Utility helpers for configuration, timezones, and validation."""

from __future__ import annotations

import pathlib
from typing import Any, Dict

import yaml


def project_root() -> pathlib.Path:
    """Return the repository root directory."""
    return pathlib.Path(__file__).resolve().parents[2]


def load_yaml(path: pathlib.Path) -> Dict[str, Any]:
    """Load a YAML file into a dictionary."""
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_config(name: str) -> Dict[str, Any]:
    """Load a configuration file from the config directory."""
    cfg_path = project_root() / "config" / f"{name}.yml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing configuration: {cfg_path}")
    return load_yaml(cfg_path)


def ensure_columns(df, required):
    """Raise if required columns are missing from a dataframe."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Dataframe missing required columns: {missing}")
