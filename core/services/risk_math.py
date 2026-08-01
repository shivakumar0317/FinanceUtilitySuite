"""Shared numeric helpers for the RMS Risk Engine."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def numeric_series(dataframe: pd.DataFrame, column: str) -> pd.Series:
    if column not in dataframe.columns:
        return pd.Series(0.0, index=dataframe.index, dtype=float)
    return pd.to_numeric(dataframe[column], errors="coerce").fillna(0.0)


def safe_sum(dataframe: pd.DataFrame, column: str, absolute: bool = False) -> float:
    series = numeric_series(dataframe, column)
    if absolute:
        series = series.abs()
    value = float(series.sum())
    return value if math.isfinite(value) else 0.0


def safe_ratio(numerator: float, denominator: float, multiplier: float = 100.0) -> float:
    if denominator == 0:
        return 0.0
    value = numerator / denominator * multiplier
    return float(value) if math.isfinite(value) else 0.0


def clamp(value: Any, minimum: float = 0.0, maximum: float = 100.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return minimum
    if not math.isfinite(numeric):
        return minimum
    return max(minimum, min(maximum, numeric))


def band_score(value: float, warning: float, critical: float) -> float:
    """
    Convert a raw percentage into a 0-100 risk score.

    0 -> no risk
    warning threshold -> 40
    critical threshold -> 70
    2 x critical threshold -> 100
    """
    value = max(float(value), 0.0)

    if critical <= warning:
        raise ValueError("Critical threshold must be greater than warning threshold.")

    if value <= warning:
        return clamp((value / warning) * 40.0 if warning else 0.0)

    if value <= critical:
        fraction = (value - warning) / (critical - warning)
        return clamp(40.0 + fraction * 30.0)

    upper = critical * 2.0
    if value >= upper:
        return 100.0

    fraction = (value - critical) / (upper - critical)
    return clamp(70.0 + fraction * 30.0)
