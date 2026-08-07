"""
Finance Utility Suite
Enterprise RMS

Module:
    historical_analytics_service.py

Description:
    Provides historical analytics and trend data
    from stored portfolio snapshots.
"""

from __future__ import annotations

import pandas as pd

from core.snapshots.snapshot_repository import SnapshotRepository


class HistoricalAnalyticsService:
    """
    Historical analytics service.

    Reads snapshot metadata and prepares
    trend data for dashboard charts.
    """

    def __init__(
        self,
        repository: SnapshotRepository | None = None,
    ) -> None:

        self.repository = repository or SnapshotRepository()

    def portfolio_history(self) -> pd.DataFrame:
        """
        Complete portfolio history.
        """

        snapshots = self.repository.list_snapshots()

        if not snapshots:
            return pd.DataFrame()

        rows = []

        for item in reversed(snapshots):

            rows.append(
                {
                    "business_date": pd.to_datetime(
                        item.business_date,
                        errors="coerce",
                    ),

                    "timestamp": pd.to_datetime(
                    item.timestamp,
                    errors="coerce",
                    ),
                    "portfolio_value": item.portfolio_value,
                    "total_exposure": item.total_exposure,
                    "total_mtm": item.total_mtm,
                    "clients": item.clients,
                    "symbols": item.symbols,
                    "risk_score": item.risk_score,
                    "health": item.health,
                    "margin_utilization": item.margin_utilization,
                    "diversification_score": item.diversification_score,
                    "top_client_concentration": (
                        item.top_client_concentration
                    ),
                    "top_symbol_concentration": (
                        item.top_symbol_concentration
                    ),
                }
            )

        return (
            pd.DataFrame(rows)
            .sort_values("business_date")
            .reset_index(drop=True)
        )

    def exposure_trend(self) -> pd.DataFrame:
        """
        Exposure trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "total_exposure",
            ]
        ].copy()

    def mtm_trend(self) -> pd.DataFrame:
        """
        MTM trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "total_mtm",
            ]
        ].copy()

    def portfolio_value_trend(self) -> pd.DataFrame:
        """
        Portfolio value trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "portfolio_value",
            ]
        ].copy()

    def client_trend(self) -> pd.DataFrame:
        """
        Client count trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "clients",
            ]
        ].copy()

    def symbol_trend(self) -> pd.DataFrame:
        """
        Symbol count trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "symbols",
            ]
        ].copy()

    def risk_score_trend(self) -> pd.DataFrame:
        """
        Risk score trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "risk_score",
            ]
        ].copy()

    def margin_utilization_trend(self) -> pd.DataFrame:
        """
        Margin utilization trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "margin_utilization",
            ]
        ].copy()

    def diversification_trend(self) -> pd.DataFrame:
        """
        Diversification score trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "diversification_score",
            ]
        ].copy()

    def concentration_trend(self) -> pd.DataFrame:
        """
        Client/Symbol concentration trend.
        """

        df = self.portfolio_history()

        if df.empty:
            return df

        return df[
            [
                "business_date",
                "top_client_concentration",
                "top_symbol_concentration",
            ]
        ].copy()

    def latest_summary(self) -> dict:
        """
        Latest snapshot summary.
        """

        df = self.portfolio_history()

        if df.empty:
            return {}

        latest = df.iloc[-1]

        return latest.to_dict()