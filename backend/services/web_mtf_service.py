from __future__ import annotations

from io import BytesIO
from threading import Lock

import numpy as np
import pandas as pd
from fastapi import UploadFile

from core.services.stock_master_service import StockMasterService

class WebMTFService:
    """MTF upload, validation and dashboard calculations."""

    REQUIRED_COLUMNS = {
        "ACCOUNTID",
        "SYMBOL",
        "NETVALUE",
        "MARKTOMARKET",
        "BUY VALUE",
        "MTF VAR",
        "MTF MARGIN",
    }

    COLUMN_ALIASES = {
        "ACCOUNT ID": "ACCOUNTID",
        "ACCOUNTID": "ACCOUNTID",
        "ACCOUNT_ID": "ACCOUNTID",
        "NET VALUE": "NETVALUE",
        "NETVALUE": "NETVALUE",
        "MARK TO MARKET": "MARKTOMARKET",
        "MARKTOMARKET": "MARKTOMARKET",
        "MTM": "MARKTOMARKET",
        "BUYVALUE": "BUY VALUE",
        "BUY VALUE": "BUY VALUE",
        "MTFVAR": "MTF VAR",
        "MTF VAR": "MTF VAR",
        "MTFMARGIN": "MTF MARGIN",
        "MTF MARGIN": "MTF MARGIN",
    }

    _datasets: dict[int, pd.DataFrame] = {}
    _lock = Lock()

    @classmethod
    def _enrich_cap_category(
        cls,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Enrich MTF rows with cached market-cap category.

        Important:
        Do NOT perform live Yahoo Finance calls during MTF upload.
        MTF upload must remain fast and should use existing Stock Master
        cache data only.
        """

        result = dataframe.copy()

        symbols = (
            result["SYMBOL"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
            .unique()
            .tolist()
        )

        if not symbols:
            result["CAP_CATEGORY"] = "Unclassified"
            return result

        stock_master = StockMasterService()
        category_map: dict[str, str] = {}

        for symbol in symbols:
            try:
                # Prefer fresh cache.
                record = stock_master.cache.get(symbol)

                # If fresh cache is unavailable, allow stale cache.
                if record is None:
                    record = stock_master.cache.get_any(symbol)

                if record:
                    category = record.get("scrip_category")

                    if not category:
                        market_cap = record.get("market_cap", 0)

                        try:
                            market_cap = float(market_cap or 0)
                        except (TypeError, ValueError):
                            market_cap = 0.0

                        from core.services.sector_classifier import SectorClassifier

                        category = SectorClassifier.classify_market_cap(
                            market_cap
                        )

                    category_map[symbol] = category or "Unclassified"

            except Exception:
                category_map[symbol] = "Unclassified"

        result["SCRIP_CATEGORY"] = (
            result["SYMBOL"]
            .map(category_map)
            .fillna("Unclassified")
        )

        return result

    @classmethod
    async def upload(
        cls,
        user_id: int,
        file: UploadFile,
    ) -> dict:
        dataframe = await cls._read_upload(file)
        normalized = cls._normalize(dataframe)
        normalized = cls._enrich_cap_category(normalized)

        with cls._lock:
            cls._datasets[user_id] = normalized

        return cls.dashboard(user_id)

    @classmethod
    def dashboard(cls, user_id: int) -> dict:
        dataframe = cls._get_dataset(user_id)

        summary = cls._summary(dataframe)
        margin_distribution = cls._margin_distribution(dataframe)
        cap_net_value_distribution = cls._cap_net_value_distribution(dataframe)
        symbol_exposure = cls._symbol_exposure(dataframe)
        top_margin_clients = cls._top_margin_clients(dataframe)
        top_margin_symbols = cls._top_margin_symbols(dataframe)
        top_mtm_gainers = cls._top_mtm(dataframe, ascending=False)
        top_mtm_losers = cls._top_mtm(dataframe, ascending=True)
        client_risk = cls._client_risk(dataframe)

        return {
            "summary": summary,
            "margin_distribution": margin_distribution,
            "cap_net_value_distribution": cap_net_value_distribution,
            "symbol_exposure": symbol_exposure,
            "top_margin_clients": top_margin_clients,
            "top_margin_symbols": top_margin_symbols,
            "top_mtm_gainers": top_mtm_gainers,
            "top_mtm_losers": top_mtm_losers,
            "client_risk": client_risk,
        }

    @classmethod
    def client_risk(cls, user_id: int) -> list[dict]:
        return cls._client_risk(cls._get_dataset(user_id))

    @classmethod
    def symbol_exposure(cls, user_id: int) -> list[dict]:
        return cls._symbol_exposure(cls._get_dataset(user_id))

    @classmethod
    def _get_dataset(cls, user_id: int) -> pd.DataFrame:
        with cls._lock:
            dataframe = cls._datasets.get(user_id)

            if dataframe is None:
                raise ValueError(
                    "Upload an MTF Excel or CSV file first."
                )

            result = dataframe.copy()

        # Backward compatibility:
        # Older saved MTF datasets do not contain CAP_CATEGORY.
        # Enrich them from the Stock Master cache when required.
        if "CAP_CATEGORY" not in result.columns:
            result = cls._enrich_cap_category(result)

        return result

    @classmethod
    async def _read_upload(
        cls,
        file: UploadFile,
    ) -> pd.DataFrame:
        filename = (file.filename or "").lower()
        content = await file.read()

        if not content:
            raise ValueError("The uploaded MTF file is empty.")

        stream = BytesIO(content)

        try:
            if filename.endswith(".csv"):
                return pd.read_csv(stream)

            if filename.endswith((".xlsx", ".xls")):
                return pd.read_excel(stream)

        except Exception as error:
            raise ValueError(
                f"Unable to read the MTF file: {error}"
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
            raise ValueError("The MTF file contains no rows.")

        normalized = dataframe.copy()
        normalized.columns = [
            cls._canonical_column(column)
            for column in normalized.columns
        ]

        missing = cls.REQUIRED_COLUMNS - set(normalized.columns)

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

        normalized["ACCOUNTID"] = (
            normalized["ACCOUNTID"]
            .astype(str)
            .str.strip()
        )
        normalized["SYMBOL"] = (
            normalized["SYMBOL"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        numeric_columns = [
            "NETVALUE",
            "MARKTOMARKET",
            "BUY VALUE",
            "MTF VAR",
            "MTF MARGIN",
        ]

        for column in numeric_columns:
            normalized[column] = pd.to_numeric(
                normalized[column],
                errors="coerce",
            ).fillna(0.0)

        normalized = normalized[
            (normalized["ACCOUNTID"] != "")
            & (normalized["SYMBOL"] != "")
        ].copy()

        if normalized.empty:
            raise ValueError(
                "No valid AccountId and Symbol rows were found."
            )

        normalized = normalized.replace(
            [np.inf, -np.inf],
            0.0,
        )

        return normalized

    @classmethod
    def _canonical_column(cls, column) -> str:
        cleaned = " ".join(
            str(column).strip().upper().split()
        )

        return cls.COLUMN_ALIASES.get(cleaned, cleaned)

    @classmethod
    def _summary(cls, dataframe: pd.DataFrame) -> dict:
        total_clients = int(dataframe["ACCOUNTID"].nunique())
        total_symbols = int(dataframe["SYMBOL"].nunique())
        total_buy_value = float(dataframe["BUY VALUE"].sum())
        total_net_value = float(dataframe["NETVALUE"].sum())
        total_mtm = float(dataframe["MARKTOMARKET"].sum())
        total_margin = float(dataframe["MTF MARGIN"].sum())

        client_group = cls._client_group(dataframe)

        positive_clients = int(
            (client_group["mtm"] > 0).sum()
        )
        negative_clients = int(
            (client_group["mtm"] < 0).sum()
        )

        average_margin_percent = float(
            client_group["margin_percent"].mean()
            if not client_group.empty
            else 0.0
        )

        risk_level = cls._overall_risk_level(
            total_buy_value=total_buy_value,
            total_mtm=total_mtm,
            average_margin_percent=average_margin_percent,
            client_risk=client_group,
        )

        return {
            "total_clients": total_clients,
            "total_symbols": total_symbols,
            "total_buy_value": round(total_buy_value, 2),
            "total_net_value": round(total_net_value, 2),
            "total_mtm": round(total_mtm, 2),
            "total_margin": round(total_margin, 2),
            "average_margin_percent": round(
                average_margin_percent,
                2,
            ),
            "positive_mtm_clients": positive_clients,
            "negative_mtm_clients": negative_clients,
            "risk_level": risk_level,
        }

    @classmethod
    def _margin_distribution(
        cls,
        dataframe: pd.DataFrame,
    ) -> list[dict]:
        clients = cls._client_group(dataframe)

        bins = [-np.inf, 15, 25, 40, 60, np.inf]
        labels = [
            "Below 15%",
            "15% - 25%",
            "25% - 40%",
            "40% - 60%",
            "Above 60%",
        ]

        clients["margin_range"] = pd.cut(
            clients["margin_percent"],
            bins=bins,
            labels=labels,
            right=False,
        )

        grouped = (
            clients.groupby(
                "margin_range",
                observed=False,
            )
            .agg(
                clients=("account_id", "count"),
                margin_value=("margin", "sum"),
            )
            .reindex(labels, fill_value=0)
            .reset_index()
        )

        return [
            {
                "range": str(row["margin_range"]),
                "clients": int(row["clients"]),
                "margin_value": round(
                    float(row["margin_value"]),
                    2,
                ),
            }
            for _, row in grouped.iterrows()
        ]

    @staticmethod
    def _cap_net_value_distribution(
        dataframe: pd.DataFrame,
    ) -> list[dict]:
        grouped = (
            dataframe.groupby(
                "SCRIP_CATEGORY",
                as_index=False,
            )
            .agg(
                net_value=("NETVALUE", "sum"),
                symbols=("SYMBOL", "nunique"),
            )
        )

        category_order = [
            "Large Cap",
            "Mid Cap",
            "Small Cap",
            "Unclassified",
        ]

        grouped["sort_order"] = (
            grouped["SCRIP_CATEGORY"]
            .map(
                {
                    category: index
                    for index, category in enumerate(
                        category_order
                    )
                }
            )
            .fillna(len(category_order))
        )

        grouped = grouped.sort_values("sort_order")

        return [
            {
                "cap_category": str(
                    row["SCRIP_CATEGORY"]
                ),
                "net_value": round(
                    float(row["net_value"]),
                    2,
                ),
                "symbols": int(row["symbols"]),
            }
            for _, row in grouped.iterrows()
        ]

    @staticmethod
    def _symbol_exposure(
        dataframe: pd.DataFrame,
    ) -> list[dict]:
        grouped = (
            dataframe.groupby(
                "SYMBOL",
                as_index=False,
            )
            .agg(
                buy_value=("BUY VALUE", "sum"),
                net_value=("NETVALUE", "sum"),
                mtm=("MARKTOMARKET", "sum"),
                margin=("MTF MARGIN", "sum"),
                clients=("ACCOUNTID", "nunique"),
            )
            .sort_values(
                "buy_value",
                ascending=False,
            )
        )

        return [
            {
                "symbol": str(row["SYMBOL"]),
                "buy_value": round(
                    float(row["buy_value"]),
                    2,
                ),
                "net_value": round(
                    float(row["net_value"]),
                    2,
                ),
                "mtm": round(float(row["mtm"]), 2),
                "margin": round(
                    float(row["margin"]),
                    2,
                ),
                "clients": int(row["clients"]),
            }
            for _, row in grouped.iterrows()
        ]

    @classmethod
    def _top_margin_clients(
        cls,
        dataframe: pd.DataFrame,
        limit: int = 10,
    ) -> list[dict]:
        grouped = cls._client_group(dataframe).sort_values(
            "margin",
            ascending=False,
        ).head(limit)

        return [
            {
                "account_id": str(row["account_id"]),
                "margin": round(float(row["margin"]), 2),
                "buy_value": round(
                    float(row["buy_value"]),
                    2,
                ),
                "net_value": round(
                    float(row["net_value"]),
                    2,
                ),
                "mtm": round(float(row["mtm"]), 2),
                "symbols": int(row["symbols"]),
            }
            for _, row in grouped.iterrows()
        ]

    @staticmethod
    def _top_margin_symbols(
        dataframe: pd.DataFrame,
        limit: int = 10,
    ) -> list[dict]:
        grouped = (
            dataframe.groupby(
                "SYMBOL",
                as_index=False,
            )
            .agg(
                margin=("MTF MARGIN", "sum"),
                buy_value=("BUY VALUE", "sum"),
                net_value=("NETVALUE", "sum"),
                mtm=("MARKTOMARKET", "sum"),
                clients=("ACCOUNTID", "nunique"),
            )
            .sort_values(
                "margin",
                ascending=False,
            )
            .head(limit)
        )

        return [
            {
                "symbol": str(row["SYMBOL"]),
                "margin": round(float(row["margin"]), 2),
                "buy_value": round(
                    float(row["buy_value"]),
                    2,
                ),
                "net_value": round(
                    float(row["net_value"]),
                    2,
                ),
                "mtm": round(float(row["mtm"]), 2),
                "clients": int(row["clients"]),
            }
            for _, row in grouped.iterrows()
        ]

    @staticmethod
    def _top_mtm(
        dataframe: pd.DataFrame,
        ascending: bool,
        limit: int = 10,
    ) -> list[dict]:
        grouped = (
            dataframe.groupby(
                ["ACCOUNTID", "SYMBOL"],
                as_index=False,
            )
            .agg(
                mtm=("MARKTOMARKET", "sum"),
                buy_value=("BUY VALUE", "sum"),
                margin=("MTF MARGIN", "sum"),
            )
            .sort_values(
                "mtm",
                ascending=ascending,
            )
            .head(limit)
        )

        return [
            {
                "account_id": str(row["ACCOUNTID"]),
                "symbol": str(row["SYMBOL"]),
                "mtm": round(float(row["mtm"]), 2),
                "buy_value": round(
                    float(row["buy_value"]),
                    2,
                ),
                "margin": round(
                    float(row["margin"]),
                    2,
                ),
            }
            for _, row in grouped.iterrows()
        ]

    @classmethod
    def _client_risk(
        cls,
        dataframe: pd.DataFrame,
    ) -> list[dict]:
        clients = cls._client_group(dataframe)

        rows = []

        for _, row in clients.iterrows():
            risk_score = cls._risk_score(
                margin_percent=float(
                    row["margin_percent"]
                ),
                mtm_percent=float(
                    row["mtm_percent"]
                ),
                symbols=int(row["symbols"]),
            )

            rows.append(
                {
                    "account_id": str(
                        row["account_id"]
                    ),
                    "buy_value": round(
                        float(row["buy_value"]),
                        2,
                    ),
                    "net_value": round(
                        float(row["net_value"]),
                        2,
                    ),
                    "mtm": round(float(row["mtm"]), 2),
                    "margin": round(
                        float(row["margin"]),
                        2,
                    ),
                    "margin_percent": round(
                        float(row["margin_percent"]),
                        2,
                    ),
                    "mtm_percent": round(
                        float(row["mtm_percent"]),
                        2,
                    ),
                    "symbols": int(row["symbols"]),
                    "risk_score": round(
                        risk_score,
                        2,
                    ),
                    "risk_level": cls._risk_level(
                        risk_score
                    ),
                }
            )

        return sorted(
            rows,
            key=lambda item: item["risk_score"],
            reverse=True,
        )

    @staticmethod
    def _client_group(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        grouped = (
            dataframe.groupby(
                "ACCOUNTID",
                as_index=False,
            )
            .agg(
                buy_value=("BUY VALUE", "sum"),
                net_value=("NETVALUE", "sum"),
                mtm=("MARKTOMARKET", "sum"),
                margin=("MTF MARGIN", "sum"),
                symbols=("SYMBOL", "nunique"),
            )
            .rename(
                columns={
                    "ACCOUNTID": "account_id",
                }
            )
        )

        denominator = grouped["buy_value"].abs().replace(
            0,
            np.nan,
        )

        grouped["margin_percent"] = (
            grouped["margin"]
            / denominator
            * 100
        ).fillna(0.0)

        grouped["mtm_percent"] = (
            grouped["mtm"]
            / denominator
            * 100
        ).fillna(0.0)

        return grouped

    @staticmethod
    def _risk_score(
        margin_percent: float,
        mtm_percent: float,
        symbols: int,
    ) -> float:
        score = 0.0

        if margin_percent >= 60:
            score += 40
        elif margin_percent >= 40:
            score += 25
        elif margin_percent >= 25:
            score += 15

        if mtm_percent <= -20:
            score += 45
        elif mtm_percent <= -10:
            score += 30
        elif mtm_percent < 0:
            score += 15

        if symbols <= 1:
            score += 15
        elif symbols <= 3:
            score += 8

        return min(score, 100.0)

    @staticmethod
    def _risk_level(score: float) -> str:
        if score >= 60:
            return "High"

        if score >= 30:
            return "Moderate"

        return "Low"

    @classmethod
    def _overall_risk_level(
        cls,
        total_buy_value: float,
        total_mtm: float,
        average_margin_percent: float,
        client_risk: pd.DataFrame,
    ) -> str:
        loss_percent = (
            abs(min(total_mtm, 0.0))
            / abs(total_buy_value)
            * 100
            if total_buy_value
            else 0.0
        )

        high_risk_clients = 0

        for _, row in client_risk.iterrows():
            score = cls._risk_score(
                margin_percent=float(
                    row["margin_percent"]
                ),
                mtm_percent=float(
                    row["mtm_percent"]
                ),
                symbols=int(row["symbols"]),
            )

            if score >= 60:
                high_risk_clients += 1

        high_risk_ratio = (
            high_risk_clients
            / len(client_risk)
            * 100
            if len(client_risk)
            else 0.0
        )

        if (
            loss_percent >= 15
            or average_margin_percent >= 50
            or high_risk_ratio >= 30
        ):
            return "High"

        if (
            loss_percent >= 5
            or average_margin_percent >= 25
            or high_risk_ratio >= 10
        ):
            return "Moderate"

        return "Low"
