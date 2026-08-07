"""
Finance Utility Suite
Enterprise RMS

Module:
    margin_calculator.py

Description:
    Calculates margin-related portfolio metrics.

Author:
    OpenAI

Version:
    3.0
"""

from __future__ import annotations

from dataclasses import dataclass

from .portfolio_calculator import PortfolioMetrics


@dataclass(slots=True)
class MarginMetrics:
    """
    Margin-related metrics.

    Attributes
    ----------
    total_margin
        Total MTF Margin.

    total_var
        Total VAR.

    margin_utilization_percent
        Margin utilization as a percentage of portfolio value.

    mtm_loss_percent
        MTM as a percentage of portfolio value.

    margin_score
        Score (0-100) based on margin utilization.
    """

    total_margin: float
    total_var: float

    margin_utilization_percent: float
    mtm_loss_percent: float

    margin_score: float


class MarginCalculator:
    """
    Calculates margin-related metrics.
    """

    @classmethod
    def calculate(
        cls,
        portfolio: PortfolioMetrics,
    ) -> MarginMetrics:
        """
        Calculate margin metrics.

        Parameters
        ----------
        portfolio
            Portfolio metrics.

        Returns
        -------
        MarginMetrics
        """

        portfolio_value = portfolio.portfolio_value

        if portfolio_value <= 0:
            return MarginMetrics(
                total_margin=portfolio.total_margin,
                total_var=portfolio.total_var,
                margin_utilization_percent=0.0,
                mtm_loss_percent=0.0,
                margin_score=0.0,
            )

        margin_utilization = (
            portfolio.total_margin
            / portfolio_value
            * 100.0
        )

        mtm_loss_percent = (
            portfolio.total_mtm
            / portfolio_value
            * 100.0
        )

        return MarginMetrics(
            total_margin=portfolio.total_margin,
            total_var=portfolio.total_var,
            margin_utilization_percent=margin_utilization,
            mtm_loss_percent=mtm_loss_percent,
            margin_score=cls._margin_score(
                margin_utilization,
            ),
        )

    @staticmethod
    def _margin_score(
        margin_utilization: float,
    ) -> float:
        """
        Convert margin utilization into a score.

        Lower utilization = Better score.
        """

        if margin_utilization <= 10:
            return 100.0

        if margin_utilization <= 20:
            return 90.0

        if margin_utilization <= 30:
            return 80.0

        if margin_utilization <= 40:
            return 70.0

        if margin_utilization <= 50:
            return 60.0

        if margin_utilization <= 60:
            return 50.0

        if margin_utilization <= 70:
            return 40.0

        if margin_utilization <= 80:
            return 30.0

        if margin_utilization <= 90:
            return 20.0

        return 10.0