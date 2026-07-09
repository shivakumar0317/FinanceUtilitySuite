"""
Finance Utility Suite
Watchlist Service

Persistent watchlist service using JSON storage.

Author : Shiva Kumar
Version: 1.10
"""

from __future__ import annotations

import json
from pathlib import Path


class WatchlistService:
    """Manage persistent stock watchlist."""

    DATA_DIR = Path("data")
    FILE_PATH = DATA_DIR / "watchlist.json"

    DEFAULT_SYMBOLS = [
        "RELIANCE",
        "TCS",
        "INFY",
        "HDFCBANK",
        "ICICIBANK",
    ]

    @classmethod
    def load_symbols(cls) -> list[str]:
        """Load watchlist symbols from JSON."""

        cls.DATA_DIR.mkdir(exist_ok=True)

        if not cls.FILE_PATH.exists():
            cls.save_symbols(cls.DEFAULT_SYMBOLS)
            return cls.DEFAULT_SYMBOLS.copy()

        try:
            with cls.FILE_PATH.open("r", encoding="utf-8") as file:
                symbols = json.load(file)

            if not isinstance(symbols, list):
                return cls.DEFAULT_SYMBOLS.copy()

            return sorted(
                {
                    str(symbol).strip().upper()
                    for symbol in symbols
                    if str(symbol).strip()
                }
            )

        except (OSError, json.JSONDecodeError):
            return cls.DEFAULT_SYMBOLS.copy()

    @classmethod
    def save_symbols(cls, symbols: list[str]) -> None:
        """Save symbols to JSON."""

        cls.DATA_DIR.mkdir(exist_ok=True)

        clean_symbols = sorted(
            {
                str(symbol).strip().upper()
                for symbol in symbols
                if str(symbol).strip()
            }
        )

        with cls.FILE_PATH.open("w", encoding="utf-8") as file:
            json.dump(clean_symbols, file, indent=4)

    @classmethod
    def add_symbol(cls, symbol: str) -> list[str]:
        """Add symbol to watchlist."""

        symbols = cls.load_symbols()
        symbol = symbol.strip().upper()

        if symbol and symbol not in symbols:
            symbols.append(symbol)

        cls.save_symbols(symbols)

        return cls.load_symbols()

    @classmethod
    def remove_symbol(cls, symbol: str) -> list[str]:
        """Remove symbol from watchlist."""

        symbols = cls.load_symbols()
        symbol = symbol.strip().upper()

        symbols = [item for item in symbols if item != symbol]

        cls.save_symbols(symbols)

        return cls.load_symbols()