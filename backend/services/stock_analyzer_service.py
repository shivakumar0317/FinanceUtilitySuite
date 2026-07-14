from __future__ import annotations

from io import BytesIO
from typing import Any

import pandas as pd
import yfinance as yf


class StockAnalyzerService:
    @classmethod
    def analyze(cls, symbol: str, period: str = "1y", interval: str = "1d") -> dict:
        resolved, ticker, info, history = cls._load(symbol, period, interval)
        close = pd.to_numeric(history["Close"], errors="coerce").dropna()

        current_price = float(close.iloc[-1])
        previous_close = float(close.iloc[-2]) if len(close) > 1 else current_price
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0.0

        details = {
            "symbol": symbol.strip().upper(),
            "resolved_symbol": resolved,
            "company_name": info.get("longName") or info.get("shortName") or symbol.upper(),
            "sector": info.get("sector") or "Unknown",
            "industry": info.get("industry") or "Unknown",
            "exchange": info.get("exchange") or info.get("fullExchangeName") or "Unknown",
            "currency": info.get("currency") or "INR",
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "market_cap": cls._number(info.get("marketCap")),
            "pe_ratio": cls._number(info.get("trailingPE")),
            "price_to_book": cls._number(info.get("priceToBook")),
            "dividend_yield": cls._percent(info.get("dividendYield")),
            "beta": cls._number(info.get("beta")),
            "roe": cls._percent(info.get("returnOnEquity")),
            "debt_to_equity": cls._number(info.get("debtToEquity")),
            "profit_margin": cls._percent(info.get("profitMargins")),
            "fifty_two_week_high": cls._number(info.get("fiftyTwoWeekHigh")),
            "fifty_two_week_low": cls._number(info.get("fiftyTwoWeekLow")),
        }

        history_rows = []
        for index, row in history.iterrows():
            if pd.isna(row.get("Close")):
                continue
            history_rows.append({
                "date": pd.Timestamp(index).strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row.get("Volume", 0) or 0),
            })

        return {
            "details": details,
            "analysis": cls._score(details),
            "history": history_rows,
        }

    @classmethod
    def export_excel(cls, symbol: str, period: str = "1y") -> BytesIO:
        result = cls.analyze(symbol, period)
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame(
                [{"Metric": key, "Value": value} for key, value in result["details"].items()]
            ).to_excel(writer, sheet_name="Stock Details", index=False)

            pd.DataFrame(
                [{"Metric": key, "Value": value}
                 for key, value in result["analysis"].items() if key != "reasons"]
            ).to_excel(writer, sheet_name="Analysis", index=False)

            pd.DataFrame({"Reasons": result["analysis"]["reasons"]}).to_excel(
                writer, sheet_name="Reasons", index=False
            )

            pd.DataFrame(result["history"]).to_excel(
                writer, sheet_name="Price History", index=False
            )

        output.seek(0)
        return output

    @classmethod
    def _load(cls, symbol: str, period: str, interval: str):
        for candidate in cls._candidates(symbol):
            try:
                ticker = yf.Ticker(candidate)
                history = ticker.history(
                    period=period,
                    interval=interval,
                    auto_adjust=False,
                )
                if history is None or history.empty:
                    continue

                info: dict[str, Any] = {}
                try:
                    info = ticker.get_info()
                except Exception:
                    pass

                return candidate, ticker, info, history
            except Exception:
                continue

        raise ValueError(f"Unable to retrieve stock data for {symbol}.")

    @classmethod
    def _score(cls, details: dict) -> dict:
        investment = 100
        risk = 0
        reasons = []

        beta = details.get("beta")
        pe = details.get("pe_ratio")
        dividend = details.get("dividend_yield")
        roe = details.get("roe")
        debt = details.get("debt_to_equity")
        margin = details.get("profit_margin")

        if beta is not None:
            if beta > 1.5:
                investment -= 25
                risk += 40
                reasons.append("High beta indicates elevated volatility.")
            elif beta > 1.2:
                investment -= 15
                risk += 20
                reasons.append("Beta is moderately above the market.")
            elif beta < 0.8:
                reasons.append("Beta suggests comparatively lower volatility.")

        if pe is not None:
            if pe > 50:
                investment -= 20
                risk += 20
                reasons.append("P/E is above 50.")
            elif pe > 30:
                investment -= 10
                reasons.append("P/E is above 30.")

        if dividend is not None:
            if dividend > 0:
                investment += 5
                reasons.append("The stock provides a dividend yield.")
            else:
                risk += 10

        if roe is not None:
            if roe >= 15:
                investment += 10
                reasons.append("ROE is at or above 15%.")
            elif roe < 5:
                investment -= 10
                risk += 10

        if debt is not None:
            normalized = debt / 100 if debt > 10 else debt
            if normalized < 0.5:
                investment += 5
                reasons.append("Debt-to-equity is below 0.5.")
            elif normalized > 1:
                investment -= 10
                risk += 20
                reasons.append("Debt-to-equity is above 1.")

        if margin is not None:
            if margin >= 15:
                investment += 5
                reasons.append("Profit margin is at or above 15%.")
            elif margin < 0:
                investment -= 15
                risk += 10
                reasons.append("Profit margin is negative.")

        investment = int(max(0, min(investment, 100)))
        risk = int(max(0, min(risk, 100)))

        risk_level = "Low" if risk <= 25 else "Moderate" if risk <= 55 else "High"
        recommendation = (
            "BUY" if investment >= 80
            else "HOLD" if investment >= 60
            else "WATCH" if investment >= 40
            else "HIGH RISK"
        )

        return {
            "investment_score": investment,
            "risk_score": risk,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "star_rating": cls._stars(investment),
            "reasons": reasons or ["Limited financial data was available for scoring."],
        }

    @staticmethod
    def _stars(score: int) -> str:
        if score >= 90:
            return "⭐⭐⭐⭐⭐"
        if score >= 75:
            return "⭐⭐⭐⭐"
        if score >= 60:
            return "⭐⭐⭐"
        if score >= 40:
            return "⭐⭐"
        return "⭐"

    @staticmethod
    def _candidates(symbol: str) -> list[str]:
        cleaned = symbol.strip().upper()
        if cleaned.startswith("^") or cleaned.endswith((".NS", ".BO")):
            return [cleaned]
        return [f"{cleaned}.NS", f"{cleaned}.BO", cleaned]

    @staticmethod
    def _number(value):
        try:
            return None if value is None else round(float(value), 4)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _percent(cls, value):
        number = cls._number(value)
        if number is None:
            return None
        return round(number * 100, 4) if -1 <= number <= 1 else number
