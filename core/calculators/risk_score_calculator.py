"""
Finance Utility Suite
Enterprise RMS

Module:
    risk_score_calculator.py

Description:
    Calculates portfolio risk scores, health,
    warnings and overall score.
"""

from __future__ import annotations

from dataclasses import dataclass

from .margin_calculator import MarginMetrics
from .concentration_calculator import ConcentrationMetrics


@dataclass(slots=True)
class RiskScoreMetrics:
    """
    Overall portfolio scoring.
    """

    exposure_score: float
    mtm_score: float
    margin_score: float

    diversification_score: float

    client_concentration_score: float
    symbol_concentration_score: float

    overall_score: float

    health: str
    health_reason: str

    warnings: list[str]


class RiskScoreCalculator:
    """
    Calculates overall portfolio score.
    """

    @classmethod
    def calculate(
        cls,
        *,
        portfolio_value: float,
        total_exposure: float,
        total_mtm: float,
        margin: MarginMetrics,
        concentration: ConcentrationMetrics,
        symbol_count: int,
    ) -> RiskScoreMetrics:

        exposure_score = cls._exposure_score(
            portfolio_value,
            total_exposure,
        )

        mtm_score = cls._mtm_score(
            margin.mtm_loss_percent,
        )

        diversification_score = cls._diversification_score(
            symbol_count,
        )

        overall = (
            exposure_score * 0.20
            + mtm_score * 0.20
            + margin.margin_score * 0.20
            + concentration.client_concentration_score * 0.20
            + concentration.symbol_concentration_score * 0.10
            + diversification_score * 0.10
        )

        health, reason = cls._health(overall)

        warnings = cls._warnings(
            margin,
            concentration,
        )

        return RiskScoreMetrics(
            exposure_score=exposure_score,
            mtm_score=mtm_score,
            margin_score=margin.margin_score,
            diversification_score=diversification_score,
            client_concentration_score=concentration.client_concentration_score,
            symbol_concentration_score=concentration.symbol_concentration_score,
            overall_score=round(overall, 2),
            health=health,
            health_reason=reason,
            warnings=warnings,
        )

    @staticmethod
    def _exposure_score(
        portfolio_value: float,
        total_exposure: float,
    ) -> float:

        if portfolio_value <= 0:
            return 0.0

        ratio = (
            total_exposure
            / portfolio_value
        )

        if ratio <= 1:
            return 100.0

        score = 100 - ((ratio - 1) * 50)

        return max(0.0, min(100.0, score))

    @staticmethod
    def _mtm_score(
        mtm_loss_percent: float,
    ) -> float:

        loss = abs(min(0.0, mtm_loss_percent))

        if loss <= 2:
            return 100.0

        if loss <= 5:
            return 90.0

        if loss <= 10:
            return 80.0

        if loss <= 15:
            return 70.0

        if loss <= 20:
            return 60.0

        if loss <= 30:
            return 40.0

        return 20.0

    @staticmethod
    def _diversification_score(
        symbols: int,
    ) -> float:

        if symbols >= 100:
            return 100.0

        if symbols >= 75:
            return 90.0

        if symbols >= 50:
            return 80.0

        if symbols >= 30:
            return 70.0

        if symbols >= 20:
            return 60.0

        return 40.0

    @staticmethod
    def _health(
        score: float,
    ) -> tuple[str, str]:

        if score >= 90:
            return (
                "Excellent",
                "Portfolio risk is very low.",
            )

        if score >= 75:
            return (
                "Good",
                "Portfolio is healthy.",
            )

        if score >= 60:
            return (
                "Moderate",
                "Portfolio requires monitoring.",
            )

        if score >= 40:
            return (
                "High Risk",
                "Portfolio concentration is high.",
            )

        return (
            "Critical",
            "Immediate action recommended.",
        )

    @staticmethod
    def _warnings(
        margin: MarginMetrics,
        concentration: ConcentrationMetrics,
    ) -> list[str]:

        warnings: list[str] = []

        if margin.margin_utilization_percent > 80:
            warnings.append(
                "High margin utilization."
            )

        if margin.mtm_loss_percent < -10:
            warnings.append(
                "Large MTM loss."
            )

        if (
            concentration.top_client_concentration_percent
            > 30
        ):
            warnings.append(
                "High client concentration."
            )

        if (
            concentration.top_symbol_concentration_percent
            > 25
        ):
            warnings.append(
                "High symbol concentration."
            )

        return warnings