"""
Finance Utility Suite
MTF Service

Business logic for Margin Trading Facility (MTF).

Author : Shiva Kumar
Version : 0.96
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class MTFService:
    """Business logic for MTF Analyzer."""

    REQUIRED_COLUMNS = [
        "AccountId",
        "Symbol",
        "BUY VALUE",
        "NetValue",
        "MarkToMarket",
        "MTF VAR",
        "MTF MARGIN",
    ]

    BUY_VALUE_LIMIT = 5_000_000
    MARGIN_LIMIT = 1_000_000
    MTM_LOSS_LIMIT = -100_000

    @classmethod
    def load(cls, file_path: str | Path):
        """
        Load and normalize an MTF file through the canonical
        MTFImportService pipeline.

        This compatibility method is retained so existing
        Desktop callers continue to work.
        """
        from core.services.mtf_import_service import MTFImportService

        import_result = MTFImportService.load_file(file_path)

        dataframe = import_result.dataframe
        summary = cls.calculate_summary(dataframe)

        return dataframe, summary

    @classmethod
    def validate_dataframe(cls, dataframe: pd.DataFrame) -> None:
        """
        Validate an already-normalized MTF dataframe.

        File loading and normalization are handled by
        MTFImportService.
        """
        if dataframe is None:
            raise ValueError("MTF dataframe cannot be None.")

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("MTF input must be a pandas DataFrame.")

        if dataframe.empty:
            raise ValueError("MTF dataframe cannot be empty.")

        missing = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                "Missing required MTF columns:\n\n"
                + "\n".join(missing)
            )

    @classmethod
    def calculate_summary(cls, dataframe: pd.DataFrame) -> dict:
        """Calculate dashboard summary."""

        total_clients = dataframe["AccountId"].nunique()
        total_positions = len(dataframe)
        buy_value = dataframe["BUY VALUE"].sum()
        market_value = dataframe["NetValue"].sum()
        mtm = dataframe["MarkToMarket"].sum()
        margin = dataframe["MTF MARGIN"].sum()
        var = dataframe["MTF VAR"].sum()

        margin_percent = cls._safe_percentage(margin, buy_value)

        return {
            "clients": total_clients,
            "positions": total_positions,
            "buy_value": buy_value,
            "market_value": market_value,
            "mtm": mtm,
            "total_mtm": mtm,
            "margin": margin,
            "var": var,
            "margin_percent": margin_percent,
            "avg_margin": round(dataframe["MTF MARGIN"].mean(), 2),
            "avg_var": round(dataframe["MTF VAR"].mean(), 2),
        }

    @classmethod
    def top_exposure(cls, dataframe: pd.DataFrame, limit: int = 10):
        """Top clients by BUY VALUE."""

        return (
            dataframe.groupby("AccountId", as_index=False)
            .agg(
                {
                    "BUY VALUE": "sum",
                    "MarkToMarket": "sum",
                    "MTF MARGIN": "sum",
                }
            )
            .sort_values(by="BUY VALUE", ascending=False)
            .head(limit)
        )

    @classmethod
    def top_mtm_gainers(cls, dataframe: pd.DataFrame, limit: int = 10):
        """Top MTM gainers."""

        return dataframe.sort_values(by="MarkToMarket", ascending=False).head(limit)

    @classmethod
    def top_mtm_losers(cls, dataframe: pd.DataFrame, limit: int = 10):
        """Top MTM losers."""

        return dataframe.sort_values(by="MarkToMarket", ascending=True).head(limit)

    @classmethod
    def symbol_exposure(cls, dataframe: pd.DataFrame, limit: int | None = None):
        """Exposure by symbol."""

        result = (
            dataframe.groupby("Symbol", as_index=False)
            .agg(
                {
                    "BUY VALUE": "sum",
                    "MarkToMarket": "sum",
                    "MTF MARGIN": "sum",
                }
            )
            .sort_values(by="BUY VALUE", ascending=False)
        )

        if limit is not None:
            return result.head(limit)

        return result

    @classmethod
    def margin_summary(cls, dataframe: pd.DataFrame) -> dict:
        """Calculate margin summary."""

        buy_value = dataframe["BUY VALUE"].sum()
        margin = dataframe["MTF MARGIN"].sum()
        var = dataframe["MTF VAR"].sum()
        margin_percent = cls._safe_percentage(margin, buy_value)

        return {
            "buy_value": buy_value,
            "margin": margin,
            "var": var,
            "margin_percent": margin_percent,
        }

    @classmethod
    def margin_distribution(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Create margin percentage distribution by client."""

        client_data = cls._client_aggregates(dataframe)

        bins = [-1, 5, 10, 20, float("inf")]
        labels = ["0-5%", "5-10%", "10-20%", ">20%"]

        client_data["Margin Bucket"] = pd.cut(
            client_data["Margin Percent"],
            bins=bins,
            labels=labels,
        )

        return (
            client_data.groupby("Margin Bucket", observed=False)
            .size()
            .reset_index(name="Clients")
        )

    @classmethod
    def top_margin_clients(
        cls,
        dataframe: pd.DataFrame,
        limit: int = 10,
    ) -> pd.DataFrame:
        """Top clients by MTF margin."""

        return (
            cls._client_aggregates(dataframe)
            .sort_values(by="MTF MARGIN", ascending=False)
            .head(limit)
        )

    @classmethod
    def top_margin_symbols(
        cls,
        dataframe: pd.DataFrame,
        limit: int = 10,
    ) -> pd.DataFrame:
        """Top symbols by MTF margin."""

        return (
            dataframe.groupby("Symbol", as_index=False)
            .agg(
                {
                    "BUY VALUE": "sum",
                    "MTF MARGIN": "sum",
                    "MarkToMarket": "sum",
                }
            )
            .sort_values(by="MTF MARGIN", ascending=False)
            .head(limit)
        )

    @classmethod
    def client_risk(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calculate client-level risk."""

        client_data = cls._client_aggregates(dataframe)

        client_data["Risk Score"] = client_data.apply(
            cls._calculate_risk_score,
            axis=1,
        )

        client_data["Risk Level"] = client_data["Risk Score"].apply(
            cls._risk_level,
        )

        return client_data.sort_values(
            by="Risk Score",
            ascending=False,
        )

    @classmethod
    def risk_summary(cls, dataframe: pd.DataFrame) -> dict:
        """Summarize client risk levels."""

        risk_data = cls.client_risk(dataframe)

        counts = risk_data["Risk Level"].value_counts()

        return {
            "low": int(counts.get("Low", 0)),
            "medium": int(counts.get("Medium", 0)),
            "high": int(counts.get("High", 0)),
        }

    @classmethod
    def _client_aggregates(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Aggregate MTF data by client."""

        client_data = (
            dataframe.groupby("AccountId", as_index=False)
            .agg(
                {
                    "BUY VALUE": "sum",
                    "MTF MARGIN": "sum",
                    "MTF VAR": "sum",
                    "MarkToMarket": "sum",
                    "NetQty": "sum",
                    "Symbol": "count",
                }
            )
            .rename(columns={"Symbol": "Positions"})
        )

        client_data["Margin Percent"] = client_data.apply(
            lambda row: cls._safe_percentage(
                row["MTF MARGIN"],
                row["BUY VALUE"],
            ),
            axis=1,
        )

        return client_data

    @classmethod
    def _calculate_risk_score(cls, row: pd.Series) -> int:
        """Calculate risk score for one client."""

        score = 0

        if row["BUY VALUE"] > cls.BUY_VALUE_LIMIT:
            score += 40

        if row["MTF MARGIN"] > cls.MARGIN_LIMIT:
            score += 30

        if row["MarkToMarket"] < cls.MTM_LOSS_LIMIT:
            score += 30

        return score

    @staticmethod
    def _risk_level(score: int) -> str:
        """Convert score to risk level."""

        if score >= 70:
            return "High"

        if score >= 40:
            return "Medium"

        return "Low"

    @staticmethod
    def _safe_percentage(numerator: float, denominator: float) -> float:
        """Safely calculate percentage."""

        if denominator == 0:
            return 0.0

        return round((numerator / denominator) * 100, 2)