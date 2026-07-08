"""
Finance Utility Suite
Market Status Service

Version: 1.10
"""

from __future__ import annotations

from datetime import datetime, time


class MarketStatusService:
    """Checks whether the Indian market is open."""

    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 30)

    @classmethod
    def is_market_open(cls) -> bool:
        now = datetime.now()

        # Saturday = 5, Sunday = 6
        if now.weekday() >= 5:
            return False

        current_time = now.time()

        return (
            cls.MARKET_OPEN
            <= current_time
            <= cls.MARKET_CLOSE
        )

    @classmethod
    def get_status_text(cls) -> str:
        return (
            "🟢 Market Open"
            if cls.is_market_open()
            else "🔴 Market Closed"
        )

    @classmethod
    def get_market_hours(cls) -> str:
        return "09:15 AM - 03:30 PM"