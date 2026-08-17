"""RMS v2.0.1 - Sector and market-cap classifier."""
from __future__ import annotations
import math
from typing import Any

class SectorClassifier:
    INR_PER_CRORE = 10_000_000.0
    ALIASES = {
        "technology": "Information Technology",
        "information technology": "Information Technology",
        "financial": "Financial Services",
        "consumer cyclical": "Consumer Discretionary",
        "consumer defensive": "Consumer Staples",
        "basic materials": "Materials",
    }

    @classmethod
    def classify_market_cap(cls, value: Any, unit: str = "rupees") -> str:
        market_cap = cls._float(value)
        if market_cap <= 0:
            return "Unclassified"
        crores = market_cap / cls.INR_PER_CRORE if unit.lower() in {"rupees", "inr", "rs"} else market_cap
        if crores >= 20_000:
            return "Large Cap"
        if crores >= 5_000:
            return "Mid Cap"
        return "Small Cap"

    @classmethod
    def normalize_sector(cls, value: Any) -> str:
        text = cls._text(value)
        return cls.ALIASES.get(text.casefold(), text) if text else "Unclassified"

    @classmethod
    def normalize_industry(cls, value: Any) -> str:
        return cls._text(value) or "Unclassified"

    @staticmethod
    def _text(value: Any) -> str:
        text = str(value or "").strip()
        return "" if text.casefold() in {"", "none", "nan", "null", "n/a"} else " ".join(text.split())

    @staticmethod
    def _float(value: Any) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0
        return 0.0 if math.isnan(number) or math.isinf(number) else number
