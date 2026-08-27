from __future__ import annotations

import pandas as pd


class WebMTFConcentrationService:
    """Web MTF concentration-risk calculations matching Desktop RMS."""

    REQUIRED_COLUMNS = {
        "ACCOUNTID",
        "SYMBOL",
        "NETVALUE",
        "MARKTOMARKET",
        "BUY VALUE",
        "MTF VAR",
        "MTF MARGIN",
    }

    @classmethod
    def calculate(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame.")

        missing = sorted(
            cls.REQUIRED_COLUMNS.difference(dataframe.columns)
        )

        if missing:
            raise ValueError(
                "Missing required columns: " + ", ".join(missing)
            )

        frame = dataframe[
            [
                "ACCOUNTID",
                "SYMBOL",
                "NETVALUE",
                "BUY VALUE",
                "MARKTOMARKET",
                "MTF VAR",
                "MTF MARGIN",
            ]
        ].copy()

        # Canonical MTFImportService already provides cleaned
        # identifiers and numeric financial columns.
        frame["ACCOUNTID"] = (
            frame["ACCOUNTID"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        frame["SYMBOL"] = (
            frame["SYMBOL"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        frame = frame[
            frame["ACCOUNTID"].ne("")
            & frame["SYMBOL"].ne("")
        ].copy()

        if frame.empty:
            return cls._empty_summary()

        # ---------------------------------------------------------
        # Aggregate once at Account + Symbol level.
        #
        # Previous implementation:
        #   Account group
        #       -> Symbol group for every account
        #
        # New implementation:
        #   One vectorized Account + Symbol groupby.
        # ---------------------------------------------------------

        symbol_summary = (
            frame.groupby(
                ["ACCOUNTID", "SYMBOL"],
                as_index=False,
                sort=False,
            )
            .agg(
                BUY_VALUE=("BUY VALUE", "sum"),
                NETVALUE=("NETVALUE", "sum"),
                MARKTOMARKET=("MARKTOMARKET", "sum"),
                MTF_VAR=("MTF VAR", "sum"),
                MTF_MARGIN=("MTF MARGIN", "sum"),
            )
        )

        symbol_summary["EXPOSURE"] = (
            symbol_summary["NETVALUE"].abs()
        )

        # ---------------------------------------------------------
        # Aggregate the Account + Symbol result to Account level.
        # ---------------------------------------------------------

        client_summary = (
            symbol_summary.groupby(
                "ACCOUNTID",
                as_index=False,
                sort=False,
            )
            .agg(
                Holdings=("SYMBOL", "nunique"),
                Total_Exposure=("EXPOSURE", "sum"),
                BUY_VALUE=("BUY_VALUE", "sum"),
                NetValue=("NETVALUE", "sum"),
                MarkToMarket=("MARKTOMARKET", "sum"),
                MTF_VAR=("MTF_VAR", "sum"),
                MTF_MARGIN=("MTF_MARGIN", "sum"),
            )
        )

        # ---------------------------------------------------------
        # Find the largest stock/exposure for every client.
        # ---------------------------------------------------------

        largest_indices = (
            symbol_summary.groupby(
                "ACCOUNTID",
                sort=False,
            )["EXPOSURE"]
            .idxmax()
        )

        largest = (
            symbol_summary.loc[
                largest_indices,
                [
                    "ACCOUNTID",
                    "SYMBOL",
                    "EXPOSURE",
                ],
            ]
            .rename(
                columns={
                    "SYMBOL": "Largest Stock",
                    "EXPOSURE": "Largest Exposure",
                }
            )
            .reset_index(drop=True)
        )

        result = client_summary.merge(
            largest,
            on="ACCOUNTID",
            how="left",
        )

        result["Largest Holding %"] = (
            result["Largest Exposure"]
            / result["Total_Exposure"]
            .replace(0, pd.NA)
            * 100
        ).fillna(0.0)

        result["Risk Level"] = result["Holdings"].map(
            cls._risk_level
        )

        result = result.rename(
            columns={
                "ACCOUNTID": "AccountId",
                "Total_Exposure": "Total Exposure",
            }
        )

        # Keep the existing API field names and rounding behavior.
        result["AccountId"] = result["AccountId"].astype(str)
        result["Largest Stock"] = (
            result["Largest Stock"]
            .fillna("")
            .astype(str)
        )

        numeric_columns = [
            "Largest Exposure",
            "Largest Holding %",
            "Total Exposure",
            "BUY_VALUE",
            "NetValue",
            "MarkToMarket",
            "MTF_VAR",
            "MTF_MARGIN",
        ]

        for column in numeric_columns:
            result[column] = result[column].astype(float).round(2)

        result = result.rename(
            columns={
                "BUY_VALUE": "BUY VALUE",
                "MTF_VAR": "MTF VAR",
                "MTF_MARGIN": "MTF MARGIN",
            }
        )

        return cls._sort_summary(result)

    @classmethod
    def get_summary(
        cls,
        summary: pd.DataFrame,
    ) -> dict[str, int | float]:
        total_clients = int(len(summary))

        single_stock_clients = int(
            (summary["Holdings"] == 1).sum()
        )

        multiple_stock_clients = int(
            (summary["Holdings"] > 1).sum()
        )

        three_to_five_stock_clients = int(
            summary["Holdings"].between(
                3,
                5,
                inclusive="both",
            ).sum()
        )

        diversified_clients = int(
            (summary["Holdings"] > 5).sum()
        )

        critical_clients = int(
            (summary["Risk Level"] == "Critical").sum()
        )

        high_risk_clients = int(
            (summary["Risk Level"] == "High").sum()
        )

        highest_concentration = (
            float(summary["Largest Holding %"].max())
            if not summary.empty
            else 0.0
        )

        total_exposure = float(
            summary["Total Exposure"].sum()
        )

        total_mtm = float(
            summary["MarkToMarket"].sum()
        )

        return {
            "total_clients": total_clients,
            "single_stock_clients": single_stock_clients,
            "multiple_stock_clients": multiple_stock_clients,
            "three_to_five_stock_clients": (
                three_to_five_stock_clients
            ),
            "diversified_clients": diversified_clients,
            "critical_clients": critical_clients,
            "high_risk_clients": high_risk_clients,
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

    @classmethod
    def single_stock_clients(
        cls,
        summary: pd.DataFrame,
    ) -> pd.DataFrame:
        return (
            summary[summary["Holdings"] == 1]
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

    @classmethod
    def top_concentrated_clients(
        cls,
        summary: pd.DataFrame,
        limit: int = 10,
    ) -> pd.DataFrame:
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
            .head(max(int(limit), 1))
            .reset_index(drop=True)
        )

    @classmethod
    def multiple_stock_clients(
        cls,
        summary: pd.DataFrame,
    ) -> pd.DataFrame:
        return (
            summary[summary["Holdings"] > 1]
            .sort_values(
                by=[
                    "Holdings",
                    "Largest Holding %",
                    "Total Exposure",
                ],
                ascending=[
                    False,
                    False,
                    False,
                ],
            )
            .reset_index(drop=True)
        )

    @staticmethod
    def distribution(
        summary: pd.DataFrame,
    ) -> list[dict]:
        return [
            {
                "category": "Single Stock",
                "clients": int(
                    (summary["Holdings"] == 1).sum()
                ),
            },
            {
                "category": "Multiple Stocks",
                "clients": int(
                    (summary["Holdings"] > 1).sum()
                ),
            },
        ]

    @staticmethod
    def risk_distribution(
        summary: pd.DataFrame,
    ) -> list[dict]:
        return [
            {
                "risk_level": level,
                "clients": int(
                    (summary["Risk Level"] == level).sum()
                ),
            }
            for level in (
                "Critical",
                "High",
                "Medium",
                "Low",
            )
        ]

    @staticmethod
    def _risk_level(holdings: int) -> str:
        if holdings <= 1:
            return "Critical"

        if holdings == 2:
            return "High"

        if holdings <= 5:
            return "Medium"

        return "Low"

    @staticmethod
    def _sort_summary(
        summary: pd.DataFrame,
    ) -> pd.DataFrame:
        risk_order = {
            "Critical": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4,
        }

        result = summary.copy()

        result["_RiskOrder"] = (
            result["Risk Level"]
            .map(risk_order)
            .fillna(99)
        )

        return (
            result.sort_values(
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
            .drop(columns=["_RiskOrder"])
            .reset_index(drop=True)
        )

    @staticmethod
    def _empty_summary() -> pd.DataFrame:
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
