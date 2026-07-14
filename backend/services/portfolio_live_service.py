from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
from threading import Lock

import pandas as pd
import yfinance as yf
from fastapi import UploadFile


class PortfolioLiveService:
    """Session-style in-memory portfolio storage for Phase 1."""

    REQUIRED_COLUMNS = {"SYMBOL", "QTY", "AVG_PRICE"}
    HISTORY_DAYS = 180

    _portfolios: dict[int, pd.DataFrame] = {}
    _lock = Lock()

    @classmethod
    async def upload(
        cls,
        user_id: int,
        file: UploadFile,
    ) -> dict:
        dataframe = await cls._read_upload(file)
        normalized = cls._normalize(dataframe)

        with cls._lock:
            cls._portfolios[user_id] = normalized

        return cls.dashboard(user_id)

    @classmethod
    def dashboard(cls, user_id: int) -> dict:
        with cls._lock:
            dataframe = cls._portfolios.get(user_id)

            if dataframe is None:
                raise ValueError(
                    "No portfolio has been uploaded for this session."
                )

            holdings = dataframe.copy()

        rows = []

        for _, holding in holdings.iterrows():
            quote = cls._quote(holding["SYMBOL"])

            quantity = float(holding["QTY"])
            average_price = float(holding["AVG_PRICE"])
            current_price = quote["price"]

            invested_value = quantity * average_price
            current_value = quantity * current_price
            profit_loss = current_value - invested_value
            profit_loss_percent = (
                profit_loss / invested_value * 100
                if invested_value
                else 0.0
            )
            today_profit_loss = quantity * quote["change"]

            rows.append(
                {
                    "symbol": holding["SYMBOL"],
                    "quantity": quantity,
                    "average_price": average_price,
                    "current_price": round(current_price, 2),
                    "invested_value": round(invested_value, 2),
                    "current_value": round(current_value, 2),
                    "profit_loss": round(profit_loss, 2),
                    "profit_loss_percent": round(
                        profit_loss_percent,
                        2,
                    ),
                    "day_change": round(
                        today_profit_loss,
                        2,
                    ),
                    "day_change_percent": round(
                        quote["change_percent"],
                        2,
                    ),
                    "resolved_symbol": quote["resolved_symbol"],
                }
            )

        total_invested = sum(
            row["invested_value"] for row in rows
        )
        total_current = sum(
            row["current_value"] for row in rows
        )
        total_profit_loss = total_current - total_invested
        total_profit_loss_percent = (
            total_profit_loss / total_invested * 100
            if total_invested
            else 0.0
        )
        today_profit_loss = sum(
            row["day_change"] for row in rows
        )

        clean_rows = [
            {
                key: value
                for key, value in row.items()
                if key != "resolved_symbol"
            }
            for row in rows
        ]

        return {
            "summary": {
                "invested_value": round(total_invested, 2),
                "current_value": round(total_current, 2),
                "profit_loss": round(total_profit_loss, 2),
                "profit_loss_percent": round(
                    total_profit_loss_percent,
                    2,
                ),
                "today_profit_loss": round(
                    today_profit_loss,
                    2,
                ),
                "total_holdings": len(rows),
            },
            "holdings": clean_rows,
            "performance": cls._performance(rows),
            "top_holdings": cls._clean_rows(
                sorted(
                    rows,
                    key=lambda item: item["current_value"],
                    reverse=True,
                )[:10]
            ),
            "top_gainers": cls._clean_rows(
                sorted(
                    rows,
                    key=lambda item: item[
                        "profit_loss_percent"
                    ],
                    reverse=True,
                )[:5]
            ),
            "top_losers": cls._clean_rows(
                sorted(
                    rows,
                    key=lambda item: item[
                        "profit_loss_percent"
                    ],
                )[:5]
            ),
        }

    @classmethod
    async def _read_upload(
        cls,
        file: UploadFile,
    ) -> pd.DataFrame:
        filename = (file.filename or "").lower()
        content = await file.read()

        if not content:
            raise ValueError("The uploaded file is empty.")

        stream = BytesIO(content)

        try:
            if filename.endswith(".csv"):
                return pd.read_csv(stream)

            if filename.endswith((".xlsx", ".xls")):
                return pd.read_excel(stream)

        except Exception as error:
            raise ValueError(
                f"Unable to read the uploaded file: {error}"
            ) from error

        raise ValueError(
            "Unsupported file type. Upload .xlsx, .xls or .csv."
        )

    @classmethod
    def _normalize(
        cls,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        if dataframe is None or dataframe.empty:
            raise ValueError("Portfolio file contains no rows.")

        normalized = dataframe.copy()
        normalized.columns = [
            str(column).strip().upper()
            for column in normalized.columns
        ]

        missing = cls.REQUIRED_COLUMNS - set(
            normalized.columns
        )

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

        normalized = normalized[
            ["SYMBOL", "QTY", "AVG_PRICE"]
        ].copy()

        normalized["SYMBOL"] = (
            normalized["SYMBOL"]
            .astype(str)
            .str.strip()
            .str.upper()
        )
        normalized["QTY"] = pd.to_numeric(
            normalized["QTY"],
            errors="coerce",
        )
        normalized["AVG_PRICE"] = pd.to_numeric(
            normalized["AVG_PRICE"],
            errors="coerce",
        )

        normalized = normalized.dropna(
            subset=["SYMBOL", "QTY", "AVG_PRICE"]
        )
        normalized = normalized[
            (normalized["SYMBOL"] != "")
            & (normalized["QTY"] > 0)
            & (normalized["AVG_PRICE"] >= 0)
        ]

        if normalized.empty:
            raise ValueError(
                "No valid holdings were found in the file."
            )

        normalized = (
            normalized.groupby(
                "SYMBOL",
                as_index=False,
            )
            .agg(
                {
                    "QTY": "sum",
                    "AVG_PRICE": "mean",
                }
            )
        )

        return normalized

    @classmethod
    def _quote(cls, symbol: str) -> dict:
        for candidate in cls._candidates(symbol):
            try:
                ticker = yf.Ticker(candidate)
                history = ticker.history(
                    period="5d",
                    interval="1d",
                    auto_adjust=False,
                )

                if history is None or history.empty:
                    continue

                close = pd.to_numeric(
                    history["Close"],
                    errors="coerce",
                ).dropna()

                if close.empty:
                    continue

                price = float(close.iloc[-1])
                previous = (
                    float(close.iloc[-2])
                    if len(close) > 1
                    else price
                )
                change = price - previous
                change_percent = (
                    change / previous * 100
                    if previous
                    else 0.0
                )

                return {
                    "resolved_symbol": candidate,
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                }

            except Exception:
                continue

        return {
            "resolved_symbol": symbol,
            "price": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
        }

    @classmethod
    def _performance(
        cls,
        rows: list[dict],
    ) -> list[dict]:
        end_date = datetime.today()
        start_date = end_date - timedelta(
            days=cls.HISTORY_DAYS
        )

        portfolio_series: pd.Series | None = None

        for row in rows:
            try:
                data = yf.download(
                    row["resolved_symbol"],
                    start=start_date.strftime("%Y-%m-%d"),
                    end=(
                        end_date + timedelta(days=1)
                    ).strftime("%Y-%m-%d"),
                    auto_adjust=True,
                    progress=False,
                    threads=False,
                )

                if data is None or data.empty:
                    continue

                close = data["Close"]

                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

                close = pd.to_numeric(
                    close,
                    errors="coerce",
                ).dropna()

                value_series = (
                    close * row["quantity"]
                )

                if portfolio_series is None:
                    portfolio_series = value_series
                else:
                    portfolio_series = (
                        portfolio_series.add(
                            value_series,
                            fill_value=0,
                        )
                    )

            except Exception:
                continue

        if (
            portfolio_series is None
            or portfolio_series.empty
        ):
            return []

        portfolio_series = (
            portfolio_series.sort_index()
            .ffill()
            .dropna()
        )

        return [
            {
                "date": pd.Timestamp(index).strftime(
                    "%Y-%m-%d"
                ),
                "value": round(float(value), 2),
            }
            for index, value in portfolio_series.items()
        ]

    @staticmethod
    def _candidates(symbol: str) -> list[str]:
        cleaned = symbol.strip().upper()

        if cleaned.endswith((".NS", ".BO")):
            return [cleaned]

        return [
            f"{cleaned}.NS",
            f"{cleaned}.BO",
            cleaned,
        ]

    @staticmethod
    def _clean_rows(rows: list[dict]) -> list[dict]:
        return [
            {
                key: value
                for key, value in row.items()
                if key != "resolved_symbol"
            }
            for row in rows
        ]
