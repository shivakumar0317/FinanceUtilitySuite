"""
Finance Utility Suite
Enterprise RMS

Module:
    concentration_calculator.py

Description:
    Calculates client and symbol concentration metrics.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from core.models.risk_summary import RiskItem


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

        portfolio_value = float(
            pd.to_numeric(
                dataframe["NetValue"],
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )

        top_clients = cls._build_items(
            dataframe,
            group_column="AccountId",
            portfolio_value=portfolio_value,
        )

        top_symbols = cls._build_items(
            dataframe,
            group_column="Symbol",
            portfolio_value=portfolio_value,
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
        portfolio_value: float,
    ) -> list[RiskItem]:

        grouped = (
            dataframe.groupby(group_column, dropna=False)
            .agg(
                exposure=("NetValue", "sum"),
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
                exposure / portfolio_value * 100
                if portfolio_value > 0
                else 0.0
            )

            score = ConcentrationCalculator._score(percent)

            items.append(
                RiskItem(
                    name=str(name),
                    exposure=exposure,
                    mtm=mtm,
                    concentration_percent=percent,
                    score=score,
                    level=ConcentrationCalculator._level(
                        percent,
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

        return max(0.0, min(100.0, score))

    @staticmethod
    def _level(
        concentration: float,
    ) -> str:

        if concentration >= 40:
            return "Critical"

        if concentration >= 30:
            return "High"

        if concentration >= 20:
            return "Moderate"

        return "Good"