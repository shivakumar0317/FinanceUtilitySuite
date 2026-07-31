"""RMS v2.0.1 - Yahoo metadata adapter with Indian exchange fallback."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import pandas as pd
import yfinance as yf

@dataclass(slots=True)
class StockMetadata:
    symbol: str
    yahoo_symbol: str
    company_name: str
    sector: str
    industry: str
    market_cap: float
    beta: float
    current_price: float
    currency: str
    exchange: str
    source: str = "Yahoo Finance"
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class YahooMetadataService:
    @classmethod
    def fetch(cls, symbol: str) -> StockMetadata:
        base = cls.normalize_symbol(symbol)
        errors = []
        for yahoo_symbol in (f"{base}.NS", f"{base}.BO", base):
            try:
                metadata = cls._fetch_candidate(base, yahoo_symbol)
                if metadata.current_price > 0 or metadata.market_cap > 0 or metadata.company_name != base:
                    return metadata
            except Exception as error:
                errors.append(f"{yahoo_symbol}: {error}")
        raise LookupError(f"Unable to enrich {base}. {'; '.join(errors[-3:])}")

    @classmethod
    def _fetch_candidate(cls, base: str, yahoo_symbol: str) -> StockMetadata:
        ticker = yf.Ticker(yahoo_symbol)
        price = cls._current_price(ticker)
        try:
            info = ticker.info if isinstance(ticker.info, dict) else {}
        except Exception:
            info = {}
        return StockMetadata(
            symbol=base,
            yahoo_symbol=yahoo_symbol,
            company_name=cls._text(info.get("longName"), info.get("shortName"), base),
            sector=cls._text(info.get("sector"), "Unclassified"),
            industry=cls._text(info.get("industry"), "Unclassified"),
            market_cap=cls._float(info.get("marketCap")),
            beta=cls._float(info.get("beta"), 1.0),
            current_price=price,
            currency=cls._text(info.get("currency"), "INR"),
            exchange=cls._text(info.get("exchange"), info.get("fullExchangeName"), ""),
        )

    @staticmethod
    def _current_price(ticker: yf.Ticker) -> float:
        try:
            fast = ticker.fast_info
            for key in ("last_price", "regular_market_price", "previous_close"):
                try:
                    value = fast[key]
                except Exception:
                    value = getattr(fast, key, None)
                price = YahooMetadataService._float(value)
                if price > 0:
                    return price
        except Exception:
            pass
        history = ticker.history(period="5d", interval="1d", auto_adjust=False, actions=False, raise_errors=True)
        if history is None or history.empty or "Close" not in history:
            return 0.0
        closes = pd.to_numeric(history["Close"], errors="coerce").dropna()
        return float(closes.iloc[-1]) if not closes.empty else 0.0

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        value = "".join(str(symbol or "").strip().upper().split())
        value = value.removesuffix(".NS").removesuffix(".BO")
        if not value:
            raise ValueError("Stock symbol cannot be empty.")
        return value

    @staticmethod
    def _text(*values: Any) -> str:
        for value in values:
            text = str(value or "").strip()
            if text and text.casefold() not in {"none", "nan", "null"}:
                return text
        return ""

    @staticmethod
    def _float(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return float(default)
        return float(default) if pd.isna(number) else number
