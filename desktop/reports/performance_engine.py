"""Reusable portfolio performance calculations for Finance Utility Suite."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Final

import pandas as pd

from desktop.reports.analytics_engine import AnalyticsDataError, PortfolioAnalyticsEngine


class PerformanceDataError(ValueError):
    """Raised when holdings or historical performance data is invalid."""


@dataclass(frozen=True)
class PerformanceSummary:
    invested_value: float
    current_value: float
    profit_loss: float
    return_pct: float
    winners: int
    losers: int
    breakeven: int
    best_stock: str
    best_stock_return_pct: float
    worst_stock: str
    worst_stock_return_pct: float
    best_sector: str
    best_sector_return_pct: float
    worst_sector: str
    worst_sector_return_pct: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PerformanceEngine:
    """Calculate holding, sector, contribution, and time-series performance."""

    VERSION: Final[str] = "1.38.1"
    HISTORY_ALIASES: Final[dict[str, tuple[str, ...]]] = {
        "Date": ("Date", "DATE", "date", "Timestamp", "As Of", "Valuation Date"),
        "Portfolio Value": (
            "Portfolio Value", "Current Value", "Market Value", "Value",
            "Closing Value", "NAV",
        ),
    }

    def __init__(self) -> None:
        self.analytics_engine = PortfolioAnalyticsEngine()

    def prepare_holdings(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Normalize holdings through the stable v1.38.0 analytics engine."""
        try:
            return self.analytics_engine.prepare(dataframe)
        except AnalyticsDataError as exc:
            raise PerformanceDataError(str(exc)) from exc

    def calculate_summary(self, dataframe: pd.DataFrame) -> PerformanceSummary:
        frame = self.prepare_holdings(dataframe)
        sectors = self.sector_performance(frame, prepared=True)
        ranked = frame.sort_values(["Return %", "Profit"], ascending=[False, False])
        best = ranked.iloc[0]
        worst = ranked.iloc[-1]
        best_sector = sectors.iloc[0]
        worst_sector = sectors.iloc[-1]
        invested = float(frame["Investment"].sum())
        current = float(frame["Current Value"].sum())
        profit = float(frame["Profit"].sum())
        return PerformanceSummary(
            invested_value=round(invested, 2),
            current_value=round(current, 2),
            profit_loss=round(profit, 2),
            return_pct=round((profit / invested * 100) if invested else 0.0, 2),
            winners=int((frame["Profit"] > 0).sum()),
            losers=int((frame["Profit"] < 0).sum()),
            breakeven=int((frame["Profit"] == 0).sum()),
            best_stock=str(best["Symbol"]),
            best_stock_return_pct=round(float(best["Return %"]), 2),
            worst_stock=str(worst["Symbol"]),
            worst_stock_return_pct=round(float(worst["Return %"]), 2),
            best_sector=str(best_sector["Sector"]),
            best_sector_return_pct=round(float(best_sector["Return %"]), 2),
            worst_sector=str(worst_sector["Sector"]),
            worst_sector_return_pct=round(float(worst_sector["Return %"]), 2),
        )

    def holding_contribution(self, dataframe: pd.DataFrame, *, prepared: bool = False) -> pd.DataFrame:
        """Return each holding's P/L and its contribution to portfolio return."""
        frame = dataframe.copy() if prepared else self.prepare_holdings(dataframe)
        invested = float(frame["Investment"].sum())
        frame["Contribution %"] = 0.0 if invested == 0 else frame["Profit"] / invested * 100
        columns = [
            "Symbol", "Sector", "Investment", "Current Value", "Profit",
            "Return %", "Allocation %", "Contribution %",
        ]
        return frame[columns].sort_values(
            ["Contribution %", "Profit"], ascending=[False, False]
        ).reset_index(drop=True)

    def top_gainers(self, dataframe: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
        if limit < 1:
            raise PerformanceDataError("The ranking limit must be at least 1.")
        frame = self.holding_contribution(dataframe)
        return frame.sort_values(["Return %", "Profit"], ascending=[False, False]).head(limit).reset_index(drop=True)

    def top_losers(self, dataframe: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
        if limit < 1:
            raise PerformanceDataError("The ranking limit must be at least 1.")
        frame = self.holding_contribution(dataframe)
        return frame.sort_values(["Return %", "Profit"], ascending=[True, True]).head(limit).reset_index(drop=True)

    def sector_performance(self, dataframe: pd.DataFrame, *, prepared: bool = False) -> pd.DataFrame:
        frame = dataframe.copy() if prepared else self.prepare_holdings(dataframe)
        sector = frame.groupby("Sector", as_index=False).agg(
            Holdings=("Symbol", "nunique"),
            Investment=("Investment", "sum"),
            **{"Current Value": ("Current Value", "sum")},
            Profit=("Profit", "sum"),
        )
        sector["Return %"] = sector["Profit"].div(sector["Investment"].replace(0, pd.NA)).mul(100).fillna(0.0)
        total_current = float(sector["Current Value"].sum())
        total_investment = float(sector["Investment"].sum())
        sector["Allocation %"] = 0.0 if total_current == 0 else sector["Current Value"] / total_current * 100
        sector["Contribution %"] = 0.0 if total_investment == 0 else sector["Profit"] / total_investment * 100
        numeric = ["Investment", "Current Value", "Profit", "Return %", "Allocation %", "Contribution %"]
        sector[numeric] = sector[numeric].round(2)
        return sector.sort_values(["Return %", "Profit"], ascending=[False, False]).reset_index(drop=True)

    def prepare_history(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe is None or dataframe.empty:
            raise PerformanceDataError("Historical performance data is empty.")
        frame = dataframe.copy()
        rename_map: dict[str, str] = {}
        for canonical, aliases in self.HISTORY_ALIASES.items():
            if canonical in frame.columns:
                continue
            match = next((alias for alias in aliases if alias in frame.columns), None)
            if match:
                rename_map[match] = canonical
        frame = frame.rename(columns=rename_map)
        missing = [column for column in ("Date", "Portfolio Value") if column not in frame.columns]
        if missing:
            raise PerformanceDataError("Missing historical columns: " + ", ".join(missing))
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
        frame["Portfolio Value"] = pd.to_numeric(frame["Portfolio Value"], errors="coerce")
        frame = frame.dropna(subset=["Date", "Portfolio Value"])
        frame = frame.loc[frame["Portfolio Value"] >= 0].copy()
        if frame.empty:
            raise PerformanceDataError("Historical data contains no valid observations.")
        # Last observation wins when more than one valuation exists for a date.
        return frame.sort_values("Date").drop_duplicates("Date", keep="last").reset_index(drop=True)

    def portfolio_growth(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        frame = self.prepare_history(dataframe)
        first = float(frame["Portfolio Value"].iloc[0])
        frame["Daily Return %"] = frame["Portfolio Value"].pct_change().mul(100).fillna(0.0)
        frame["Cumulative Return %"] = 0.0 if first == 0 else (frame["Portfolio Value"] / first - 1.0) * 100
        frame[["Daily Return %", "Cumulative Return %"]] = frame[["Daily Return %", "Cumulative Return %"]].round(4)
        return frame

    def monthly_returns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        frame = self.prepare_history(dataframe).set_index("Date")
        monthly = frame["Portfolio Value"].resample("ME").last().dropna().to_frame()
        monthly["Return %"] = monthly["Portfolio Value"].pct_change().mul(100).fillna(0.0)
        monthly = monthly.reset_index()
        monthly["Period"] = monthly["Date"].dt.strftime("%Y-%m")
        return monthly[["Period", "Date", "Portfolio Value", "Return %"]].round({"Portfolio Value": 2, "Return %": 4})

    def yearly_returns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        frame = self.prepare_history(dataframe).set_index("Date")
        yearly = frame["Portfolio Value"].resample("YE").last().dropna().to_frame()
        yearly["Return %"] = yearly["Portfolio Value"].pct_change().mul(100).fillna(0.0)
        yearly = yearly.reset_index()
        yearly["Year"] = yearly["Date"].dt.year
        return yearly[["Year", "Date", "Portfolio Value", "Return %"]].round({"Portfolio Value": 2, "Return %": 4})

    def cagr(self, dataframe: pd.DataFrame) -> float:
        frame = self.prepare_history(dataframe)
        start_date = frame["Date"].iloc[0]
        end_date = frame["Date"].iloc[-1]
        start_value = float(frame["Portfolio Value"].iloc[0])
        end_value = float(frame["Portfolio Value"].iloc[-1])
        years = (end_date - start_date).days / 365.2425
        if years <= 0:
            raise PerformanceDataError("CAGR requires at least two different valuation dates.")
        if start_value <= 0 or end_value < 0:
            raise PerformanceDataError("CAGR requires a positive starting value and non-negative ending value.")
        return round(((end_value / start_value) ** (1 / years) - 1) * 100, 4)
