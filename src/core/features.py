"""Feature engineering helpers for daily/weekly signals."""

from __future__ import annotations

import pandas as pd
import ta


def _ensure_price_columns(df: pd.DataFrame) -> None:
    required = {"open", "high", "low", "close", "volume"}
    if not required.issubset(df.columns):
        missing = required.difference(df.columns)
        raise ValueError(f"Missing columns for feature construction: {missing}")


def _compute_features(df: pd.DataFrame) -> pd.DataFrame:
    df["returns_5d"] = df["close"].pct_change(5)
    df["returns_20d"] = df["close"].pct_change(20)
    df["rsi_14"] = ta.momentum.rsi(df["close"], window=14)
    df["macd"] = ta.trend.macd_diff(df["close"])
    df["vol_20d"] = df["returns_5d"].rolling(20).std() * (252 ** 0.5)
    df["atr_14"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14)
    df["ma100"] = df["close"].rolling(100).mean()
    df["ma200"] = df["close"].rolling(200).mean()
    df["trend_100_over_200"] = (df["ma100"] > df["ma200"]).astype(float)
    return df


def build_features(prices: pd.DataFrame) -> pd.DataFrame:
    """Create technical features required by the model for each symbol."""
    if isinstance(prices.index, pd.MultiIndex) and "symbol" in prices.index.names:
        frames = []
        for symbol, symbol_prices in prices.groupby(level="symbol"):
            symbol_prices = symbol_prices.droplevel("symbol")
            _ensure_price_columns(symbol_prices)
            df = _compute_features(symbol_prices.copy())
            df["symbol"] = symbol
            df = df.dropna()
            df = df.set_index("symbol", append=True)
            frames.append(df)
        if not frames:
            return pd.DataFrame()
        features = pd.concat(frames)
        features.index.set_names(["date", "symbol"], inplace=True)
        return features.sort_index()

    if isinstance(prices.columns, pd.MultiIndex):
        symbols = [sym for sym in prices.columns.get_level_values(0).unique() if sym != "cash_proxy"]
        frames = []
        for symbol in symbols:
            symbol_prices = prices[symbol].copy()
            _ensure_price_columns(symbol_prices)
            df = _compute_features(symbol_prices.copy())
            df["symbol"] = symbol
            df = df.dropna()
            df = df.set_index("symbol", append=True)
            frames.append(df)
        if not frames:
            return pd.DataFrame()
        features = pd.concat(frames)
        features.index.set_names(["date", "symbol"], inplace=True)
        return features.sort_index()

    _ensure_price_columns(prices)
    df = _compute_features(prices.copy())
    return df.dropna()


def build_labels(prices: pd.DataFrame) -> pd.Series:
    """Binary label: next 5d excess return vs cash proxy for each symbol."""
    if isinstance(prices.index, pd.MultiIndex) and "symbol" in prices.index.names:
        frames = []
        base = prices.reset_index()
        cash = base.drop_duplicates("date").set_index("date")["cash_proxy"]
        for symbol, symbol_prices in prices.groupby(level="symbol"):
            symbol_prices = symbol_prices.droplevel("symbol")
            forward_return = symbol_prices["close"].pct_change(periods=5).shift(-5)
            cash_return = cash.pct_change(periods=5).shift(-5)
            label = (forward_return > cash_return).astype(int)
            label = label.dropna().to_frame(name="label")
            label["symbol"] = symbol
            label = label.set_index("symbol", append=True)
            frames.append(label["label"])
        if not frames:
            return pd.Series(dtype=int)
        labels = pd.concat(frames)
        labels.index.set_names(["date", "symbol"], inplace=True)
        return labels

    if isinstance(prices.columns, pd.MultiIndex):
        cash = prices.get(("cash_proxy", "close"))
        if cash is None:
            raise ValueError("cash_proxy close prices required for label computation")
        frames = []
        for symbol in [sym for sym in prices.columns.get_level_values(0).unique() if sym != "cash_proxy"]:
            symbol_prices = prices[symbol]
            forward_return = symbol_prices["close"].pct_change(periods=5).shift(-5)
            cash_return = cash.pct_change(periods=5).shift(-5)
            label = (forward_return > cash_return).astype(int)
            label = label.dropna().to_frame(name="label")
            label["symbol"] = symbol
            label = label.set_index("symbol", append=True)
            frames.append(label["label"])
        if not frames:
            return pd.Series(dtype=int)
        labels = pd.concat(frames).swaplevel().sort_index()
        labels.index.set_names(["date", "symbol"], inplace=True)
        return labels

    if "cash_proxy" not in prices.columns:
        raise ValueError("cash_proxy column required for label computation")
    forward_return = prices["close"].pct_change(periods=5).shift(-5)
    cash_return = prices["cash_proxy"].pct_change(periods=5).shift(-5)
    label = (forward_return > cash_return).astype(int)
    return label.dropna()
