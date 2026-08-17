"""Client and symbol concentration calculations for the central Risk Engine."""

from __future__ import annotations

import pandas as pd

from core.models.risk_summary import RiskItem
from core.services.risk_config import RiskThresholds
from core.services.risk_math import band_score, numeric_series, safe_ratio


class RiskConcentrationService:
    @staticmethod
    def _prepared(dataframe: pd.DataFrame) -> pd.DataFrame:
        frame = dataframe.copy()

        if "BUY VALUE" in frame.columns:
            frame["_Exposure"] = numeric_series(
                frame,
                "BUY VALUE",
            ).abs()
        elif "Exposure" in frame.columns:
            frame["_Exposure"] = numeric_series(
                frame,
                "Exposure",
            ).abs()
        else:
            frame["_Exposure"] = numeric_series(
                frame,
                "NetValue",
            ).abs()

        frame["_MTM"] = numeric_series(frame, "MarkToMarket")

        if "AccountId" not in frame.columns:
            frame["AccountId"] = ""
        if "Symbol" not in frame.columns:
            frame["Symbol"] = ""

        frame["AccountId"] = frame["AccountId"].fillna("").astype(str).str.strip()
        frame["Symbol"] = (
            frame["Symbol"].fillna("").astype(str).str.strip().str.upper()
        )
        return frame

    @classmethod
    def group_summary(
        cls,
        dataframe: pd.DataFrame,
        group_column: str,
    ) -> pd.DataFrame:
        frame = cls._prepared(dataframe)
        frame = frame[frame[group_column] != ""].copy()

        if frame.empty:
            return pd.DataFrame(
                columns=[group_column, "Exposure", "MTM", "Concentration %"]
            )

        result = (
            frame.groupby(group_column, as_index=False)
            .agg(Exposure=("_Exposure", "sum"), MTM=("_MTM", "sum"))
            .sort_values("Exposure", ascending=False)
            .reset_index(drop=True)
        )

        total = float(result["Exposure"].sum())
        result["Concentration %"] = result["Exposure"].apply(
            lambda value: safe_ratio(float(value), total)
        )
        return result

    @classmethod
    def top_concentration_percent(
        cls,
        dataframe: pd.DataFrame,
        group_column: str,
    ) -> float:
        summary = cls.group_summary(dataframe, group_column)
        if summary.empty:
            return 0.0
        return float(summary.iloc[0]["Concentration %"])

    @classmethod
    def score(
        cls,
        dataframe: pd.DataFrame,
        group_column: str,
        warning: float,
        critical: float,
    ) -> float:
        value = cls.top_concentration_percent(dataframe, group_column)
        return band_score(value, warning, critical)

    @classmethod
    def top_items(
        cls,
        dataframe: pd.DataFrame,
        group_column: str,
        thresholds: RiskThresholds,
        limit: int,
    ) -> list[RiskItem]:
        summary = cls.group_summary(
            dataframe,
            group_column,
        ).head(limit)

        if group_column == "AccountId":
            warning = thresholds.client_concentration_warning_percent
            critical = thresholds.client_concentration_critical_percent
        else:
            warning = thresholds.symbol_concentration_warning_percent
            critical = thresholds.symbol_concentration_critical_percent

        items: list[RiskItem] = []

        for _, row in summary.iterrows():
            name = str(row[group_column])
            exposure = float(row["Exposure"])
            mtm = float(row["MTM"])
            concentration = float(row["Concentration %"])

            score = band_score(
                concentration,
                warning,
                critical,
            )

            level = (
                "Critical"
                if concentration >= critical
                else "Warning"
                if concentration >= warning
                else "Healthy"
            )

            items.append(
                RiskItem(
                    name=name,
                    exposure=round(exposure, 2),
                    mtm=round(mtm, 2),
                    concentration_percent=round(
                        concentration,
                        2,
                    ),
                    score=round(score, 2),
                    level=level,
                )
            )

        return items
