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

        frame = dataframe.copy()

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

        numeric_columns = [
            "NETVALUE",
            "BUY VALUE",
            "MARKTOMARKET",
            "MTF VAR",
            "MTF MARGIN",
        ]

        for column in numeric_columns:
            frame[column] = pd.to_numeric(
                frame[column],
                errors="coerce",
            ).fillna(0.0)

        frame = frame[
            (frame["ACCOUNTID"] != "")
            & (frame["SYMBOL"] != "")
        ].copy()

        if frame.empty:
            return cls._empty_summary()

        rows: list[dict] = []

        for account_id, client_df in frame.groupby(
            "ACCOUNTID",
            sort=False,
        ):
            symbol_summary = (
                client_df.groupby(
                    "SYMBOL",
                    as_index=False,
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

            holdings = int(
                symbol_summary["SYMBOL"].nunique()
            )

            total_buy_value = float(
                symbol_summary["BUY_VALUE"].sum()
            )

            total_net_value = float(
                symbol_summary["NETVALUE"].sum()
            )

            total_mtm = float(
                symbol_summary["MARKTOMARKET"].sum()
            )

            total_var = float(
                symbol_summary["MTF_VAR"].sum()
            )

            total_margin = float(
                symbol_summary["MTF_MARGIN"].sum()
            )

            total_exposure = float(
                symbol_summary["EXPOSURE"].sum()
            )

            largest_stock = ""
            largest_exposure = 0.0

            if not symbol_summary.empty:
                largest_row = symbol_summary.loc[
                    symbol_summary["EXPOSURE"].idxmax()
                ]

                largest_stock = str(
                    largest_row["SYMBOL"]
                )

                largest_exposure = float(
                    largest_row["EXPOSURE"]
                )

            largest_holding_percent = (
                largest_exposure / total_exposure * 100
                if total_exposure > 0
                else 0.0
            )

            risk_level = cls._risk_level(holdings)

            rows.append(
                {
                    "AccountId": str(account_id),
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

        result = pd.DataFrame(rows)

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
