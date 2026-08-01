"""Mark-to-market portfolio risk calculations."""

from __future__ import annotations

import pandas as pd

from core.services.risk_config import RiskThresholds
from core.services.risk_math import band_score, safe_ratio, safe_sum


class MTMRiskService:
    @staticmethod
    def total_mtm(dataframe: pd.DataFrame) -> float:
        return safe_sum(dataframe, "MarkToMarket")

    @classmethod
    def mtm_loss_percent(cls, dataframe: pd.DataFrame, exposure: float) -> float:
        total_mtm = cls.total_mtm(dataframe)
        loss = abs(min(total_mtm, 0.0))
        return safe_ratio(loss, exposure)

    @classmethod
    def score(
        cls,
        dataframe: pd.DataFrame,
        exposure: float,
        thresholds: RiskThresholds,
    ) -> float:
        percent = cls.mtm_loss_percent(dataframe, exposure)
        return band_score(
            percent,
            thresholds.mtm_warning_percent,
            thresholds.mtm_critical_percent,
        )
