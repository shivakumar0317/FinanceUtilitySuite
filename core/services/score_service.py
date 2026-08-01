"""Weighted overall RMS score calculation."""

from __future__ import annotations

from core.services.risk_config import RiskWeights
from core.services.risk_math import clamp


class ScoreService:
    @staticmethod
    def calculate(
        *,
        exposure_score: float,
        mtm_score: float,
        margin_score: float,
        client_concentration_score: float,
        symbol_concentration_score: float,
        weights: RiskWeights,
    ) -> float:
        weights.validate()

        score = (
            exposure_score * weights.exposure
            + mtm_score * weights.mtm
            + margin_score * weights.margin
            + client_concentration_score * weights.client_concentration
            + symbol_concentration_score * weights.symbol_concentration
        )
        return round(clamp(score), 2)

    @staticmethod
    def diversification_score(
        client_concentration_score: float,
        symbol_concentration_score: float,
    ) -> float:
        concentration_risk = (
            float(client_concentration_score)
            + float(symbol_concentration_score)
        ) / 2.0
        return round(clamp(100.0 - concentration_risk), 2)
