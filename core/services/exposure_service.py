"""Portfolio exposure calculations."""

from __future__ import annotations

import pandas as pd

from core.services.risk_math import band_score, safe_sum


class ExposureService:
    @staticmethod
    def total_exposure(dataframe: pd.DataFrame) -> float:
        if "Exposure" in dataframe.columns:
            return safe_sum(dataframe, "Exposure", absolute=True)
        return safe_sum(dataframe, "NetValue", absolute=True)

    @staticmethod
    def portfolio_value(dataframe: pd.DataFrame) -> float:
        # For the current MTF dataset, gross exposure is the most reliable
        # portfolio-value proxy.
        return ExposureService.total_exposure(dataframe)

    @staticmethod
    def score(dataframe: pd.DataFrame) -> float:
        """
        Structural exposure score.

        This foundation version avoids hard-coded rupee-size limits because
        acceptable exposure depends on broker capital and limits. It assigns
        zero when exposure exists and 100 only when the data is invalid/empty.
        Capital-limit based exposure scoring will be added in Sprint 4.1.
        """
        return 0.0 if ExposureService.total_exposure(dataframe) > 0 else 100.0
