from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

from backend.services.portfolio_live_service import PortfolioLiveService


class WebRiskAnalyticsService:
    BENCHMARK_SYMBOL = "^NSEI"
    RISK_FREE_RATE = 0.06
    TRADING_DAYS = 252
    PERIOD_DAYS = {"6mo": 183, "1y": 365, "2y": 730, "5y": 1825}

    @classmethod
    def dashboard(cls, user_id: int, period: str = "1y") -> dict:
        holdings = cls._get_holdings(user_id)
        if period not in cls.PERIOD_DAYS:
            raise ValueError("Unsupported period. Use 6mo, 1y, 2y or 5y.")

        end_date = datetime.today()
        start_date = end_date - timedelta(days=cls.PERIOD_DAYS[period])
        rows = cls._prepare_rows(holdings)
        prices = cls._download_price_frame(rows, start_date, end_date)
        benchmark = cls._download_close(cls.BENCHMARK_SYMBOL, start_date, end_date)

        if prices.empty or benchmark.empty:
            raise ValueError("Unable to retrieve enough historical price data.")

        portfolio_values = cls._portfolio_values(prices, rows)
        aligned = pd.concat(
            [portfolio_values.rename("portfolio"), benchmark.rename("benchmark")],
            axis=1,
            join="inner",
        ).dropna()

        if len(aligned) < 20:
            raise ValueError("Not enough aligned history to calculate risk metrics.")

        returns = aligned.pct_change().dropna()
        p_returns = returns["portfolio"]
        b_returns = returns["benchmark"]

        beta = cls._beta(p_returns, b_returns)
        volatility = cls._volatility(p_returns)
        alpha = cls._alpha(p_returns, b_returns)
        sharpe = cls._sharpe(p_returns)
        drawdown = cls._drawdown(aligned["portfolio"])
        max_drawdown = float(drawdown.min() * 100)

        current_values = cls._current_values(rows)
        total_current = sum(item["current_value"] for item in current_values)
        concentration = cls._concentration(current_values, total_current)
        diversification = max(0.0, 100.0 - concentration)

        return {
            "summary": {
                "portfolio_beta": round(beta, 4),
                "volatility": round(volatility, 2),
                "alpha": round(alpha, 2),
                "sharpe_ratio": round(sharpe, 4),
                "max_drawdown": round(max_drawdown, 2),
                "concentration_risk": round(concentration, 2),
                "diversification_score": round(diversification, 2),
                "risk_level": cls._risk_level(beta, volatility),
                "benchmark_symbol": cls.BENCHMARK_SYMBOL,
                "analysis_period": period,
            },
            "performance": cls._performance(aligned),
            "drawdown": [
                {
                    "date": pd.Timestamp(index).strftime("%Y-%m-%d"),
                    "drawdown": round(float(value * 100), 2),
                }
                for index, value in drawdown.items()
            ],
            "sector_exposure": cls._sector_exposure(current_values, total_current),
            "top_risk_holdings": cls._top_risk_holdings(
                current_values, prices, b_returns, total_current
            ),
        }

    @classmethod
    def _get_holdings(cls, user_id: int) -> pd.DataFrame:
        with PortfolioLiveService._lock:
            holdings = PortfolioLiveService._portfolios.get(user_id)
            if holdings is None:
                raise ValueError("Upload a portfolio in Portfolio Live first.")
            return holdings.copy()

    @classmethod
    def _prepare_rows(cls, holdings: pd.DataFrame) -> list[dict]:
        rows = []
        for _, item in holdings.iterrows():
            symbol = str(item["SYMBOL"]).strip().upper()
            resolved = cls._resolve_symbol(symbol)
            metadata = cls._metadata(resolved)
            rows.append(
                {
                    "symbol": symbol,
                    "resolved_symbol": resolved,
                    "quantity": float(item["QTY"]),
                    "average_price": float(item["AVG_PRICE"]),
                    "sector": metadata["sector"],
                    "beta": metadata["beta"],
                }
            )
        return rows

    @classmethod
    def _download_price_frame(cls, rows, start_date, end_date) -> pd.DataFrame:
        data = {}
        for row in rows:
            close = cls._download_close(row["resolved_symbol"], start_date, end_date)
            if not close.empty:
                data[row["symbol"]] = close
        return pd.concat(data, axis=1).sort_index().ffill().dropna(how="all") if data else pd.DataFrame()

    @staticmethod
    def _download_close(symbol, start_date, end_date) -> pd.Series:
        try:
            data = yf.download(
                symbol,
                start=start_date.strftime("%Y-%m-%d"),
                end=(end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            if data is None or data.empty:
                return pd.Series(dtype=float)
            close = data["Close"]
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            return pd.to_numeric(close, errors="coerce").dropna()
        except Exception:
            return pd.Series(dtype=float)

    @staticmethod
    def _portfolio_values(prices: pd.DataFrame, rows: list[dict]) -> pd.Series:
        values = pd.Series(0.0, index=prices.index)
        for row in rows:
            if row["symbol"] in prices.columns:
                values = values.add(prices[row["symbol"]] * row["quantity"], fill_value=0)
        return values.replace([np.inf, -np.inf], np.nan).dropna()

    @staticmethod
    def _beta(portfolio_returns, benchmark_returns) -> float:
        aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1, join="inner").dropna()
        if aligned.empty:
            return 0.0
        variance = aligned.iloc[:, 1].var()
        return 0.0 if not variance else float(aligned.iloc[:, 0].cov(aligned.iloc[:, 1]) / variance)

    @classmethod
    def _volatility(cls, returns) -> float:
        return 0.0 if returns.empty else float(returns.std() * np.sqrt(cls.TRADING_DAYS) * 100)

    @classmethod
    def _alpha(cls, portfolio_returns, benchmark_returns) -> float:
        aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1, join="inner").dropna()
        if aligned.empty:
            return 0.0
        return float((aligned.iloc[:, 0].mean() - aligned.iloc[:, 1].mean()) * cls.TRADING_DAYS * 100)

    @classmethod
    def _sharpe(cls, returns) -> float:
        if returns.empty:
            return 0.0
        annual_return = returns.mean() * cls.TRADING_DAYS
        annual_vol = returns.std() * np.sqrt(cls.TRADING_DAYS)
        return 0.0 if not annual_vol else float((annual_return - cls.RISK_FREE_RATE) / annual_vol)

    @staticmethod
    def _drawdown(values: pd.Series) -> pd.Series:
        return (values / values.cummax() - 1).fillna(0.0)

    @classmethod
    def _current_values(cls, rows: list[dict]) -> list[dict]:
        output = []
        for row in rows:
            price = cls._latest_price(row["resolved_symbol"])
            output.append({**row, "current_price": price, "current_value": row["quantity"] * price})
        return output

    @staticmethod
    def _concentration(rows, total) -> float:
        if not rows or not total:
            return 0.0
        return float(max(item["current_value"] for item in rows) / total * 100)

    @staticmethod
    def _performance(aligned: pd.DataFrame) -> list[dict]:
        normalized = aligned / aligned.iloc[0] * 100
        return [
            {
                "date": pd.Timestamp(index).strftime("%Y-%m-%d"),
                "portfolio": round(float(row["portfolio"]), 2),
                "benchmark": round(float(row["benchmark"]), 2),
            }
            for index, row in normalized.iterrows()
        ]

    @staticmethod
    def _sector_exposure(rows, total) -> list[dict]:
        sectors = {}
        for row in rows:
            sector = row["sector"] or "Unknown"
            sectors[sector] = sectors.get(sector, 0.0) + row["current_value"]
        return [
            {
                "sector": sector,
                "value": round(value, 2),
                "weight_percent": round(value / total * 100 if total else 0.0, 2),
            }
            for sector, value in sorted(sectors.items(), key=lambda item: item[1], reverse=True)
        ]

    @classmethod
    def _top_risk_holdings(cls, rows, price_frame, benchmark_returns, total) -> list[dict]:
        output = []
        for row in rows:
            weight = row["current_value"] / total if total else 0.0
            beta = row.get("beta")
            volatility = None
            if row["symbol"] in price_frame.columns:
                returns = price_frame[row["symbol"]].pct_change().dropna()
                if not returns.empty:
                    volatility = float(returns.std() * np.sqrt(cls.TRADING_DAYS) * 100)
                    if beta is None:
                        beta = cls._beta(returns, benchmark_returns)
            risk_contribution = abs(beta or 0.0) * weight * 100
            if volatility is not None:
                risk_contribution += volatility * weight
            output.append(
                {
                    "symbol": row["symbol"],
                    "current_value": round(row["current_value"], 2),
                    "portfolio_weight": round(weight * 100, 2),
                    "beta": round(float(beta), 4) if beta is not None else None,
                    "annualized_volatility": round(volatility, 2) if volatility is not None else None,
                    "risk_contribution": round(risk_contribution, 2),
                    "sector": row["sector"],
                }
            )
        return sorted(output, key=lambda item: item["risk_contribution"], reverse=True)[:10]

    @staticmethod
    def _risk_level(beta: float, volatility: float) -> str:
        if beta > 1.2 or volatility > 25:
            return "High"
        if beta >= 0.8 or volatility >= 15:
            return "Moderate"
        return "Low"

    @classmethod
    def _resolve_symbol(cls, symbol: str) -> str:
        for candidate in cls._candidates(symbol):
            if cls._latest_price(candidate) > 0:
                return candidate
        return symbol

    @staticmethod
    def _candidates(symbol: str) -> list[str]:
        cleaned = symbol.strip().upper()
        return [cleaned] if cleaned.endswith((".NS", ".BO")) else [f"{cleaned}.NS", f"{cleaned}.BO", cleaned]

    @staticmethod
    def _latest_price(symbol: str) -> float:
        try:
            history = yf.Ticker(symbol).history(period="5d", auto_adjust=False)
            if history is None or history.empty:
                return 0.0
            close = pd.to_numeric(history["Close"], errors="coerce").dropna()
            return 0.0 if close.empty else float(close.iloc[-1])
        except Exception:
            return 0.0

    @staticmethod
    def _metadata(symbol: str) -> dict:
        sector = "Unknown"
        beta = None
        try:
            info = yf.Ticker(symbol).get_info()
            sector = info.get("sector") or info.get("industry") or "Unknown"
            if info.get("beta") is not None:
                beta = float(info["beta"])
        except Exception:
            pass
        return {"sector": sector, "beta": beta}
