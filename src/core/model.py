"""Model training and inference interfaces."""

from __future__ import annotations

import pathlib
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from xgboost import XGBClassifier

from .features import build_features, build_labels

MODEL_PATH = pathlib.Path(__file__).resolve().parents[2] / "models" / "latest.pkl"


def train_model(prices: pd.DataFrame, cfg: Dict[str, Any]) -> Tuple[XGBClassifier, Dict[str, Any]]:
    """Train an XGBoost classifier using the configured features."""
    features = build_features(prices)
    labels = build_labels(prices)
    labels = labels.reindex(features.index).dropna()
    features = features.loc[labels.index]
    if features.empty:
        raise ValueError("No features available for training. Check your data inputs.")
    x = features[cfg["features"]]
    y = labels

    if cfg["train"].get("cv") == "time_series_split":
        tscv = TimeSeriesSplit(n_splits=5)
        best_score = -np.inf
        best_model = None
        for train_idx, valid_idx in tscv.split(x):
            model = XGBClassifier(
                n_estimators=cfg["train"].get("n_estimators", 200),
                max_depth=cfg["train"].get("max_depth", 4),
                learning_rate=cfg["train"].get("learning_rate", 0.05),
                subsample=cfg["train"].get("subsample", 0.8),
                colsample_bytree=cfg["train"].get("colsample_bytree", 0.8),
                eval_metric="logloss",
                tree_method="hist",
            )
            model.fit(x.iloc[train_idx], y.iloc[train_idx])
            score = model.score(x.iloc[valid_idx], y.iloc[valid_idx])
            if score > best_score:
                best_score = score
                best_model = model
        assert best_model is not None
        model = best_model
    else:
        x_train, x_valid, y_train, y_valid = train_test_split(
            x, y, test_size=cfg["train"].get("test_size", 0.2), shuffle=False
        )
        model = XGBClassifier(
            n_estimators=cfg["train"].get("n_estimators", 200),
            max_depth=cfg["train"].get("max_depth", 4),
            learning_rate=cfg["train"].get("learning_rate", 0.05),
            eval_metric="logloss",
            tree_method="hist",
        )
        model.fit(x_train, y_train, eval_set=[(x_valid, y_valid)], verbose=False)
    metadata = {"features": cfg["features"], "threshold": cfg["threshold"]}
    return model, metadata


def save_model(model: XGBClassifier, metadata: Dict[str, Any], path: pathlib.Path = MODEL_PATH) -> None:
    """Persist the model and metadata to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "metadata": metadata}, path)


def load_model(path: pathlib.Path = MODEL_PATH) -> Dict[str, Any]:
    """Load the persisted model bundle."""
    if not path.exists():
        raise FileNotFoundError("Model file not found. Train a model first.")
    return joblib.load(path)


def infer_proba(bundle: Dict[str, Any], features: pd.DataFrame) -> pd.Series:
    """Run inference and return probability of positive class."""
    model = bundle["model"]
    cols = bundle["metadata"]["features"]
    probs = model.predict_proba(features[cols])[:, 1]
    return pd.Series(probs, index=features.index)
