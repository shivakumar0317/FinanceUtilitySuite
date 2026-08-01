"""MTF margin and utilization calculations."""

from __future__ import annotations

import pandas as pd

from core.services.risk_config import RiskThresholds
from core.services.risk_math import band_score, safe_ratio, safe_sum


class MarginService:
    @staticmethod
    def total_margin(dataframe: pd.DataFrame) -> float:
        return safe_sum(dataframe, "MTF MARGIN", absolute=True)

    @staticmethod
    def total_var(dataframe: pd.DataFrame) -> float:
        return safe_sum(dataframe, "MTF VAR", absolute=True)

    @classmethod
    def utilization_percent(cls, dataframe: pd.DataFrame, exposure: float) -> float:
        return safe_ratio(cls.total_margin(dataframe), exposure)

    @classmethod
    def score(
        cls,
        dataframe: pd.DataFrame,
        exposure: float,
        thresholds: RiskThresholds,
    ) -> float:
        utilization = cls.utilization_percent(dataframe, exposure)
        return band_score(
            utilization,
            thresholds.margin_warning_percent,
            thresholds.margin_critical_percent,
        )
