"""
Finance Utility Suite
Concentration Risk Service

Analyzes client stock concentration for MTF accounts.

Author  : Shiva Kumar
Version : 1.30
"""

from __future__ import annotations

import pandas as pd


class ConcentrationService:
    """Service for calculating MTF client concentration risk."""

    REQUIRED_COLUMNS = [
        "AccountId",
        "Symbol",
        "BUY VALUE",
        "NetValue",
        "MarkToMarket",
        "MTF VAR",
        "MTF MARGIN",
    ]

    NUMERIC_COLUMNS = [
        "BUY VALUE",
        "NetValue",
        "MarkToMarket",
        "MTF VAR",
        "MTF MARGIN",
    ]

    def __init__(self) -> None:
        self.dataframe = pd.DataFrame()
        self.summary_df = pd.DataFrame()

    def load_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """Validate and load the MTF dataframe."""

        self.validate_dataframe(dataframe)

        self.dataframe = dataframe.copy()
        self.summary_df = pd.DataFrame()

        return self.dataframe

    def validate_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """Validate whether all required MTF columns are available."""

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "Expected a pandas DataFrame."
            )

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

    def calculate_concentration(
        self,
    ) -> pd.DataFrame:
        """
        Calculate concentration details for every MTF client.

        Returns one row per AccountId.
        """

        if self.dataframe.empty:
            raise ValueError(
                "No MTF data loaded."
            )

        dataframe = self._prepare_dataframe(
            self.dataframe
        )

        if dataframe.empty:
            self.summary_df = self._empty_summary()
            return self.summary_df

        client_rows: list[dict] = []

        for account_id, client_df in dataframe.groupby(
            "AccountId",
            sort=False,
        ):
            symbol_summary = (
                client_df.groupby(
                    "Symbol",
                    as_index=False,
                )
                .agg(
                    BuyValue=(
                        "BUY VALUE",
                        "sum",
                    ),
                    NetValue=(
                        "NetValue",
                        "sum",
                    ),
                    MarkToMarket=(
                        "MarkToMarket",
                        "sum",
                    ),
                    MTF_VAR=(
                        "MTF VAR",
                        "sum",
                    ),
                    MTF_MARGIN=(
                        "MTF MARGIN",
                        "sum",
                    ),
                )
            )

            symbol_summary["ExposureValue"] = (
                symbol_summary["NetValue"].abs()
            )

            holdings = int(
                symbol_summary["Symbol"].nunique()
            )

            total_buy_value = float(
                symbol_summary["BuyValue"].sum()
            )

            total_net_value = float(
                symbol_summary["NetValue"].sum()
            )

            total_mtm = float(
                symbol_summary["MarkToMarket"].sum()
            )

            total_var = float(
                symbol_summary["MTF_VAR"].sum()
            )

            total_margin = float(
                symbol_summary["MTF_MARGIN"].sum()
            )

            total_exposure = float(
                symbol_summary["ExposureValue"].sum()
            )

            largest_stock = ""
            largest_exposure = 0.0

            if not symbol_summary.empty:
                largest_row = symbol_summary.loc[
                    symbol_summary[
                        "ExposureValue"
                    ].idxmax()
                ]

                largest_stock = str(
                    largest_row["Symbol"]
                )

                largest_exposure = float(
                    largest_row["ExposureValue"]
                )

            largest_holding_percent = 0.0

            if total_exposure > 0:
                largest_holding_percent = (
                    largest_exposure
                    / total_exposure
                    * 100
                )

            risk_level = self._get_risk_level(
                holdings=holdings,
                largest_holding_percent=(
                    largest_holding_percent
                ),
            )

            client_rows.append(
                {
                    "AccountId": account_id,
                    "Holdings": holdings,
                    "Largest Stock": largest_stock,
                    "Largest Exposure": round(
                        largest_exposure,
                        2,
                    ),
                    "Largest Holding %": round(
                        largest_holding_percent,
                        2,
                    ),
                    "Total Exposure": round(
                        total_exposure,
                        2,
                    ),
                    "BUY VALUE": round(
                        total_buy_value,
                        2,
                    ),
                    "NetValue": round(
                        total_net_value,
                        2,
                    ),
                    "MarkToMarket": round(
                        total_mtm,
                        2,
                    ),
                    "MTF VAR": round(
                        total_var,
                        2,
                    ),
                    "MTF MARGIN": round(
                        total_margin,
                        2,
                    ),
                    "Risk Level": risk_level,
                }
            )

        self.summary_df = pd.DataFrame(
            client_rows
        )

        self.summary_df = self._sort_summary(
            self.summary_df
        )

        return self.summary_df.copy()

    def get_single_stock_clients(
        self,
    ) -> pd.DataFrame:
        """Return clients holding exactly one distinct stock."""

        summary = self._ensure_summary()

        return (
            summary[
                summary["Holdings"] == 1
            ]
            .sort_values(
                by=[
                    "Total Exposure",
                    "Largest Holding %",
                ],
                ascending=[
                    False,
                    False,
                ],
            )
            .reset_index(drop=True)
        )

    def get_two_stock_clients(
        self,
    ) -> pd.DataFrame:
        """Return clients holding exactly two distinct stocks."""

        summary = self._ensure_summary()

        return (
            summary[
                summary["Holdings"] == 2
            ]
            .sort_values(
                by=[
                    "Largest Holding %",
                    "Total Exposure",
                ],
                ascending=[
                    False,
                    False,
                ],
            )
            .reset_index(drop=True)
        )

    def get_top_concentrated_clients(
        self,
        limit: int = 20,
    ) -> pd.DataFrame:
        """Return the highest concentrated client accounts."""

        summary = self._ensure_summary()

        limit = max(int(limit), 1)

        return (
            summary.sort_values(
                by=[
                    "Largest Holding %",
                    "Total Exposure",
                ],
                ascending=[
                    False,
                    False,
                ],
            )
            .head(limit)
            .reset_index(drop=True)
        )

    def get_summary(
        self,
    ) -> dict[str, int | float]:
        """Return KPI values for the concentration dashboard."""

        summary = self._ensure_summary()

        total_clients = int(
            len(summary)
        )

        single_stock_clients = int(
            (summary["Holdings"] == 1).sum()
        )

        multiple_stock_clients = int(
            (summary["Holdings"] > 1).sum()
        )

        medium_concentration_clients = int(
            summary["Holdings"]
            .between(
                3,
                5,
                inclusive="both",
            )
            .sum()
        )

        diversified_clients = int(
            (summary["Holdings"] > 5).sum()
        )

        critical_clients = int(
            (
                summary["Risk Level"]
                == "Critical"
            ).sum()
        )

        high_risk_clients = int(
            (
                summary["Risk Level"]
                == "High"
            ).sum()
        )

        highest_concentration = 0.0

        if not summary.empty:
            highest_concentration = float(
                summary[
                    "Largest Holding %"
                ].max()
            )

        total_exposure = float(
            summary["Total Exposure"].sum()
        )

        total_mtm = float(
            summary["MarkToMarket"].sum()
        )

        return {
            "total_clients": total_clients,
            "single_stock_clients": (
                single_stock_clients
            ),
            "multiple_stock_clients": (
                multiple_stock_clients
            ),
            "three_to_five_stock_clients": (
                medium_concentration_clients
            ),
            "diversified_clients": (
                diversified_clients
            ),
            "critical_clients": (
                critical_clients
            ),
            "high_risk_clients": (
                high_risk_clients
            ),
            "highest_concentration_percent": round(
                highest_concentration,
                2,
            ),
            "total_exposure": round(
                total_exposure,
                2,
            ),
            "total_mtm": round(
                total_mtm,
                2,
            ),
        }

    def get_distribution(
        self,
    ) -> pd.DataFrame:
        """Return client distribution based on number of holdings."""

        summary = self._ensure_summary()

        distribution = pd.DataFrame(
            [
                {
                    "Category": "1 Stock",
                    "Clients": int(
                        (
                            summary["Holdings"]
                            == 1
                        ).sum()
                    ),
                    "Risk Level": "Critical",
                },
                {
                    "Category": "2 Stocks",
                    "Clients": int(
                        (
                            summary["Holdings"]
                            == 2
                        ).sum()
                    ),
                    "Risk Level": "High",
                },
                {
                    "Category": "3-5 Stocks",
                    "Clients": int(
                        summary["Holdings"]
                        .between(
                            3,
                            5,
                            inclusive="both",
                        )
                        .sum()
                    ),
                    "Risk Level": "Medium",
                },
                {
                    "Category": "6-10 Stocks",
                    "Clients": int(
                        summary["Holdings"]
                        .between(
                            6,
                            10,
                            inclusive="both",
                        )
                        .sum()
                    ),
                    "Risk Level": "Low",
                },
                {
                    "Category": "Above 10 Stocks",
                    "Clients": int(
                        (
                            summary["Holdings"]
                            > 10
                        ).sum()
                    ),
                    "Risk Level": "Low",
                },
            ]
        )

        return distribution

    def get_client_holdings(
        self,
        account_id: str,
    ) -> pd.DataFrame:
        """Return symbol-level holdings for one client."""

        if self.dataframe.empty:
            raise ValueError(
                "No MTF data loaded."
            )

        account_id = str(
            account_id
        ).strip()

        dataframe = self._prepare_dataframe(
            self.dataframe
        )

        client_df = dataframe[
            dataframe["AccountId"]
            == account_id
        ].copy()

        if client_df.empty:
            return pd.DataFrame(
                columns=[
                    "Symbol",
                    "BUY VALUE",
                    "NetValue",
                    "Exposure",
                    "MarkToMarket",
                    "MTF VAR",
                    "MTF MARGIN",
                    "Holding %",
                ]
            )

        holdings = (
            client_df.groupby(
                "Symbol",
                as_index=False,
            )
            .agg(
                {
                    "BUY VALUE": "sum",
                    "NetValue": "sum",
                    "MarkToMarket": "sum",
                    "MTF VAR": "sum",
                    "MTF MARGIN": "sum",
                }
            )
        )

        holdings["Exposure"] = (
            holdings["NetValue"].abs()
        )

        total_exposure = float(
            holdings["Exposure"].sum()
        )

        if total_exposure > 0:
            holdings["Holding %"] = (
                holdings["Exposure"]
                / total_exposure
                * 100
            )
        else:
            holdings["Holding %"] = 0.0

        numeric_columns = [
            "BUY VALUE",
            "NetValue",
            "Exposure",
            "MarkToMarket",
            "MTF VAR",
            "MTF MARGIN",
            "Holding %",
        ]

        holdings[numeric_columns] = (
            holdings[numeric_columns]
            .round(2)
        )

        return (
            holdings.sort_values(
                by="Exposure",
                ascending=False,
            )
            .reset_index(drop=True)
        )

    def _prepare_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """Clean and normalize source MTF data."""

        dataframe = dataframe.copy()

        for column in self.NUMERIC_COLUMNS:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            ).fillna(0.0)

        dataframe["AccountId"] = (
            dataframe["AccountId"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        dataframe["Symbol"] = (
            dataframe["Symbol"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        invalid_symbols = {
            "",
            "NAN",
            "NONE",
            "NULL",
        }

        dataframe = dataframe[
            (dataframe["AccountId"] != "")
            & (
                ~dataframe["Symbol"]
                .isin(invalid_symbols)
            )
        ].copy()

        return dataframe

    def _get_risk_level(
        self,
        holdings: int,
        largest_holding_percent: float,
    ) -> str:
        """Assign the initial concentration risk category."""

        if holdings <= 1:
            return "Critical"

        if holdings == 2:
            return "High"

        if holdings <= 5:
            return "Medium"

        return "Low"

    def _ensure_summary(
        self,
    ) -> pd.DataFrame:
        """Calculate concentration summary when not already available."""

        if self.summary_df.empty:
            return self.calculate_concentration()

        return self.summary_df.copy()

    @staticmethod
    def _sort_summary(
        summary_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Sort clients by risk, concentration, and exposure."""

        if summary_df.empty:
            return summary_df

        risk_order = {
            "Critical": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4,
        }

        summary_df = summary_df.copy()

        summary_df["_RiskOrder"] = (
            summary_df["Risk Level"]
            .map(risk_order)
            .fillna(99)
        )

        summary_df = (
            summary_df.sort_values(
                by=[
                    "_RiskOrder",
                    "Largest Holding %",
                    "Total Exposure",
                ],
                ascending=[
                    True,
                    False,
                    False,
                ],
            )
            .drop(
                columns=[
                    "_RiskOrder",
                ]
            )
            .reset_index(drop=True)
        )

        return summary_df

    @staticmethod
    def _empty_summary(
    ) -> pd.DataFrame:
        """Return an empty concentration summary with expected columns."""

        return pd.DataFrame(
            columns=[
                "AccountId",
                "Holdings",
                "Largest Stock",
                "Largest Exposure",
                "Largest Holding %",
                "Total Exposure",
                "BUY VALUE",
                "NetValue",
                "MarkToMarket",
                "MTF VAR",
                "MTF MARGIN",
                "Risk Level",
            ]
        )