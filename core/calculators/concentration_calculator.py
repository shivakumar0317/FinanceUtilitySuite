"""
Finance Utility Suite
Enterprise RMS

Module:
    concentration_calculator.py

Description:
    Calculates client and symbol concentration metrics.

Author:
    Shiva Kumar

Version:
    3.1
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from core.models.risk_summary import RiskItem
from core.config.risk_thresholds import DEFAULT_RISK_THRESHOLDS


@dataclass(slots=True)
class ConcentrationMetrics:
    """
    Client/Symbol concentration metrics.
    """

    top_clients: list[RiskItem]
    top_symbols: list[RiskItem]

    top_client_concentration_percent: float
    top_symbol_concentration_percent: float

    client_concentration_score: float
    symbol_concentration_score: float


class ConcentrationCalculator:
    """
    Calculates concentration statistics.
    """

    @classmethod
    def calculate(
        cls,
        dataframe: pd.DataFrame,
    ) -> ConcentrationMetrics:
        """
        Calculate client and symbol concentration.

        Enterprise RMS exposure is based on BUY VALUE.
        """

        portfolio_exposure = float(
            pd.to_numeric(
                dataframe["BUY VALUE"],
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

        top_clients = cls._build_items(
            dataframe,
            group_column="AccountId",
            portfolio_exposure=portfolio_exposure,
            thresholds=DEFAULT_RISK_THRESHOLDS.client_concentration,
        )

        top_symbols = cls._build_items(
            dataframe,
            group_column="Symbol",
            portfolio_exposure=portfolio_exposure,
            thresholds=DEFAULT_RISK_THRESHOLDS.symbol_concentration,
        )

        top_client_percent = (
            top_clients[0].concentration_percent
            if top_clients
            else 0.0
        )

        top_symbol_percent = (
            top_symbols[0].concentration_percent
            if top_symbols
            else 0.0
        )

        return ConcentrationMetrics(
            top_clients=top_clients,
            top_symbols=top_symbols,
            top_client_concentration_percent=top_client_percent,
            top_symbol_concentration_percent=top_symbol_percent,
            client_concentration_score=cls._score(
                top_client_percent,
            ),
            symbol_concentration_score=cls._score(
                top_symbol_percent,
            ),
        )

    @staticmethod
    def _build_items(
        dataframe: pd.DataFrame,
        *,
        group_column: str,
        portfolio_exposure: float,
        thresholds,
    ) -> list[RiskItem]:
        """
        Build concentration items for clients or symbols.

        Exposure is based on BUY VALUE so that it matches
        PortfolioCalculator's enterprise exposure definition.
        """

        grouped = (
            dataframe.groupby(
                group_column,
                dropna=False,
            )
            .agg(
                exposure=("BUY VALUE", "sum"),
                mtm=("MarkToMarket", "sum"),
            )
            .sort_values(
                "exposure",
                ascending=False,
            )
        )

        items: list[RiskItem] = []

        for name, row in grouped.head(10).iterrows():

            exposure = float(row["exposure"])
            mtm = float(row["mtm"])

            percent = (
                exposure / portfolio_exposure * 100
                if portfolio_exposure > 0
                else 0.0
            )

            score = ConcentrationCalculator._score(
                percent,
            )

            items.append(
                RiskItem(
                    name=str(name),
                    exposure=exposure,
                    mtm=mtm,
                    concentration_percent=percent,
                    score=score,
                    level=ConcentrationCalculator._level(
                        percent,
                        thresholds,
                    ),
                )
            )

        return items

    @staticmethod
    def _score(
        concentration: float,
    ) -> float:
        """
        Lower concentration = better score.
        """

        score = 100.0 - (concentration * 2.0)

        return max(
            0.0,
            min(100.0, score),
        )

    @staticmethod
    def _level(
        concentration: float,
        thresholds,
    ) -> str:
        if concentration >= thresholds.critical_min:
            return "Critical"

        if concentration >= thresholds.good_max:
            return "Moderate"

        return "Good"