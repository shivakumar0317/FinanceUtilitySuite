"""Core portfolio analytics for Finance Utility Suite."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Final

import pandas as pd


class AnalyticsDataError(ValueError):
    """Raised when analytics input cannot be normalized safely."""


@dataclass(frozen=True)
class AnalyticsSummary:
    total_investment: float
    current_value: float
    profit_loss: float
    return_pct: float
    holdings_count: int
    sector_count: int
    largest_holding_symbol: str
    largest_holding_value: float
    largest_holding_pct: float
    average_position_value: float
    profitable_holdings: int
    loss_making_holdings: int
    portfolio_health_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PortfolioAnalyticsEngine:
    """Normalize holdings data and calculate reusable portfolio KPIs."""

    VERSION: Final[str] = "1.38.0"
    COLUMN_ALIASES: Final[dict[str, tuple[str, ...]]] = {
        "Symbol": ("Symbol", "SYMBOL", "symbol", "Stock", "Scrip"),
        "Quantity": ("Quantity", "QTY", "Qty", "quantity", "NetQty"),
        "Average Price": ("Average Price", "Avg Price", "AVG PRICE", "Buy Price", "Purchase Price"),
        "Current Price": ("Current Price", "LTP", "Market Price", "Last Price"),
        "Investment": ("Investment", "Invested Value", "Investment Value", "Cost Value", "Buy Value"),
        "Current Value": ("Current Value", "Market Value", "Present Value"),
        "Profit": ("Profit", "Profit / Loss", "P/L", "PnL", "Unrealized P/L"),
        "Return %": ("Return %", "Return Percent", "P/L %", "Profit %"),
        "Sector": ("Sector", "Industry", "Category"),
    }
    REQUIRED_COLUMNS: Final[tuple[str, ...]] = ("Symbol", "Quantity", "Average Price", "Current Price")

    def prepare(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe is None or dataframe.empty:
            raise AnalyticsDataError("Analytics data is empty.")

        frame = dataframe.copy()
        rename_map: dict[str, str] = {}
        for canonical, aliases in self.COLUMN_ALIASES.items():
            if canonical in frame.columns:
                continue
            match = next((name for name in aliases if name in frame.columns), None)
            if match:
                rename_map[match] = canonical
        frame = frame.rename(columns=rename_map)

        missing = [column for column in self.REQUIRED_COLUMNS if column not in frame.columns]
        if missing:
            raise AnalyticsDataError("Missing required analytics columns: " + ", ".join(missing))

        for column in ("Quantity", "Average Price", "Current Price", "Investment", "Current Value", "Profit", "Return %"):
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)

        frame["Symbol"] = frame["Symbol"].fillna("").astype(str).str.strip().str.upper()
        frame = frame.loc[frame["Symbol"] != ""].copy()
        if frame.empty:
            raise AnalyticsDataError("Analytics data contains no valid symbols.")

        frame["Sector"] = (
            frame.get("Sector", pd.Series("Unclassified", index=frame.index))
            .fillna("Unclassified").astype(str).str.strip().replace("", "Unclassified")
        )
        if "Investment" not in frame.columns:
            frame["Investment"] = frame["Quantity"] * frame["Average Price"]
        if "Current Value" not in frame.columns:
            frame["Current Value"] = frame["Quantity"] * frame["Current Price"]
        if "Profit" not in frame.columns:
            frame["Profit"] = frame["Current Value"] - frame["Investment"]

        grouped = frame.groupby("Symbol", as_index=False).agg({
            "Sector": "first", "Quantity": "sum", "Investment": "sum",
            "Current Value": "sum", "Profit": "sum"
        })
        grouped["Average Price"] = grouped["Investment"].div(grouped["Quantity"].replace(0, pd.NA)).fillna(0.0)
        grouped["Current Price"] = grouped["Current Value"].div(grouped["Quantity"].replace(0, pd.NA)).fillna(0.0)
        grouped["Return %"] = grouped["Profit"].div(grouped["Investment"].replace(0, pd.NA)).mul(100).fillna(0.0)
        total_value = float(grouped["Current Value"].sum())
        grouped["Allocation %"] = 0.0 if total_value == 0 else grouped["Current Value"] / total_value * 100
        return grouped.sort_values("Current Value", ascending=False).reset_index(drop=True)

    def summarize(self, dataframe: pd.DataFrame) -> AnalyticsSummary:
        frame = self.prepare(dataframe)
        invested = float(frame["Investment"].sum())
        current = float(frame["Current Value"].sum())
        profit = float(frame["Profit"].sum())
        return_pct = (profit / invested * 100) if invested else 0.0
        largest = frame.iloc[0]
        holdings = int(len(frame))
        sectors = int(frame["Sector"].nunique())
        largest_pct = float(largest["Allocation %"])
        profitable = int((frame["Profit"] > 0).sum())
        losing = int((frame["Profit"] < 0).sum())
        health = self._health_score(return_pct, largest_pct, holdings, sectors, profitable)
        return AnalyticsSummary(
            total_investment=round(invested, 2), current_value=round(current, 2),
            profit_loss=round(profit, 2), return_pct=round(return_pct, 2),
            holdings_count=holdings, sector_count=sectors,
            largest_holding_symbol=str(largest["Symbol"]),
            largest_holding_value=round(float(largest["Current Value"]), 2),
            largest_holding_pct=round(largest_pct, 2),
            average_position_value=round(current / holdings if holdings else 0.0, 2),
            profitable_holdings=profitable, loss_making_holdings=losing,
            portfolio_health_score=health,
        )

    @staticmethod
    def _health_score(return_pct: float, largest_pct: float, holdings: int, sectors: int, profitable: int) -> float:
        score = 50.0
        score += max(-20.0, min(20.0, return_pct))
        score += min(10.0, holdings * 1.25)
        score += min(10.0, sectors * 2.0)
        score += min(10.0, profitable * 1.5)
        if largest_pct > 50:
            score -= 20
        elif largest_pct > 35:
            score -= 10
        elif largest_pct > 25:
            score -= 5
        return round(max(0.0, min(100.0, score)), 1)
