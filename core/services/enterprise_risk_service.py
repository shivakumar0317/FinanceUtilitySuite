"""
Finance Utility Suite
Enterprise RMS

Module:
    enterprise_risk_service.py

Description:
    Enterprise risk engine that orchestrates all
    calculators and produces a RiskSummary.
"""

from __future__ import annotations

from core.calculators.portfolio_calculator import (
    PortfolioCalculator,
)
from core.calculators.margin_calculator import (
    MarginCalculator,
)
from core.calculators.concentration_calculator import (
    ConcentrationCalculator,
)
from core.calculators.risk_score_calculator import (
    RiskScoreCalculator,
)

from core.models.risk_summary import (
    RiskAlert,
    RiskSummary,
)


class EnterpriseRiskService:
    """
    Enterprise Risk Engine.
    """

    @classmethod
    def analyze(cls, dataframe):

        portfolio = PortfolioCalculator.calculate(
            dataframe,
        )

        margin = MarginCalculator.calculate(
            portfolio,
        )

        concentration = (
            ConcentrationCalculator.calculate(
                dataframe,
            )
        )

        score = RiskScoreCalculator.calculate(
            portfolio_value=portfolio.portfolio_value,
            total_exposure=portfolio.total_exposure,
            total_mtm=portfolio.total_mtm,
            margin=margin,
            concentration=concentration,
            symbol_count=portfolio.symbols,
        )

        alerts = []

        for warning in score.warnings:

            alerts.append(
                RiskAlert(
                    level="Warning",
                    title=warning,
                    message=warning,
                    recommendation="Review portfolio exposure.",
                )
            )

        return RiskSummary(

            overall_score=score.overall_score,

            health=score.health,

            health_reason=score.health_reason,

            records=portfolio.records,

            clients=portfolio.clients,

            symbols=portfolio.symbols,

            portfolio_value=portfolio.portfolio_value,

            total_exposure=portfolio.total_exposure,

            total_mtm=portfolio.total_mtm,

            total_var=portfolio.total_var,

            total_margin=portfolio.total_margin,

            mtm_loss_percent=margin.mtm_loss_percent,

            margin_utilization_percent=margin.margin_utilization_percent,

            top_client_concentration_percent=(
                concentration.top_client_concentration_percent
            ),

            top_symbol_concentration_percent=(
                concentration.top_symbol_concentration_percent
            ),

            exposure_score=score.exposure_score,

            mtm_score=score.mtm_score,

            margin_score=score.margin_score,

            client_concentration_score=(
                score.client_concentration_score
            ),

            symbol_concentration_score=(
                score.symbol_concentration_score
            ),

            diversification_score=(
                score.diversification_score
            ),

            calculated_score=score.overall_score,

            display_score=round(
                score.overall_score,
                1,
            ),

            top_clients=concentration.top_clients,

            top_symbols=concentration.top_symbols,

            warnings=score.warnings,

            alerts=alerts,
        )