from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pandas as pd

@dataclass(slots=True)
class MTFImportResult:
    dataframe: pd.DataFrame
    source_file: str
    records_received: int
    records_after_cleaning: int
    clients: int
    symbols: int


class MTFImportService:
    """
    Common MTF import and normalization service.

    This is the canonical MTF input pipeline shared by
    Desktop and Web RMS workflows.
    """

    REQUIRED_COLUMNS = (
        "AccountId",
        "Symbol",
        "NetValue",
        "NetQty",
        "MarkToMarket",
        "BUY VALUE",
        "MTF VAR",
        "MTF MARGIN",
    )

    PRESERVED_COLUMNS = (
        "AccountId",
        "Exchg-Seg",
        "Symbol",
        "Instrument Name",
        "Product Type",
        "NetValue",
        "NetBuyQty",
        "NetSellQty",
        "NetQty",
        "LastTradedPrice",
        "BuyAvgPrice",
        "MarkToMarket",
        "BUY VALUE",
        "MTF VAR",
        "MTF MARGIN",
    )

    NUMERIC_COLUMNS = (
        "NetValue",
        "NetBuyQty",
        "NetSellQty",
        "NetQty",
        "LastTradedPrice",
        "BuyAvgPrice",
        "MarkToMarket",
        "BUY VALUE",
        "MTF VAR",
        "MTF MARGIN",
    )

    COLUMN_ALIASES = {
        "ACCOUNT ID": "AccountId",
        "ACCOUNTID": "AccountId",
        "ACCOUNT_ID": "AccountId",

        "SYMBOL": "Symbol",

        "NET VALUE": "NetValue",
        "NETVALUE": "NetValue",

        "NET BUY QTY": "NetBuyQty",
        "NETBUYQTY": "NetBuyQty",

        "NET SELL QTY": "NetSellQty",
        "NETSELLQTY": "NetSellQty",

        "NET QTY": "NetQty",
        "NETQTY": "NetQty",

        "LAST TRADED PRICE": "LastTradedPrice",
        "LASTTRADEDPRICE": "LastTradedPrice",
        "LTP": "LastTradedPrice",

        "BUY AVG PRICE": "BuyAvgPrice",
        "BUYAVGPRICE": "BuyAvgPrice",

        "MARK TO MARKET": "MarkToMarket",
        "MARKTOMARKET": "MarkToMarket",
        "MTM": "MarkToMarket",

        "BUYVALUE": "BUY VALUE",
        "BUY VALUE": "BUY VALUE",

        "MTFVAR": "MTF VAR",
        "MTF VAR": "MTF VAR",

        "MTFMARGIN": "MTF MARGIN",
        "MTF MARGIN": "MTF MARGIN",

        "EXCHG-SEG": "Exchg-Seg",
        "EXCHG SEG": "Exchg-Seg",

        "INSTRUMENT NAME": "Instrument Name",
        "PRODUCT TYPE": "Product Type",
    }

    @classmethod
    def load_file(
        cls,
        path: str | Path,
    ) -> MTFImportResult:
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"MTF file not found: {path}"
            )

        suffix = path.suffix.lower()

        if suffix in {".xlsx", ".xls"}:
            dataframe = pd.read_excel(path)
        elif suffix == ".csv":
            dataframe = pd.read_csv(path)
        else:
            raise ValueError(
                "Unsupported MTF file format. "
                "Please use Excel (.xlsx/.xls) or CSV."
            )

        return cls.import_dataframe(
            dataframe,
            source_file=path.name,
        )

    @classmethod
    def load_bytes(
        cls,
        content: bytes,
        filename: str,
    ) -> MTFImportResult:
        if not content:
            raise ValueError("The selected MTF file is empty.")

        suffix = Path(filename).suffix.lower()

        stream = BytesIO(content)

        if suffix in {".xlsx", ".xls"}:
            dataframe = pd.read_excel(stream)
        elif suffix == ".csv":
            dataframe = pd.read_csv(stream)
        else:
            raise ValueError(
                "Unsupported MTF file format. "
                "Please use Excel (.xlsx/.xls) or CSV."
            )

        return cls.import_dataframe(
            dataframe,
            source_file=filename,
        )

    @classmethod
    def import_dataframe(
        cls,
        dataframe: pd.DataFrame,
        source_file: str = "In-memory DataFrame",
    ) -> MTFImportResult:
        if dataframe is None:
            raise ValueError(
                "MTF dataframe cannot be None."
            )

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "MTF input must be a pandas DataFrame."
            )

        if dataframe.empty:
            raise ValueError(
                "The selected MTF file does not contain any data."
            )

        dataframe = cls._normalize_columns(dataframe)

        missing = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                "The selected MTF file is missing required columns:\n\n"
                + "\n".join(
                    f"• {column}"
                    for column in missing
                )
            )

        cleaned = cls._clean_dataframe(dataframe)

        if cleaned.empty:
            raise ValueError(
                "No valid MTF records remain after cleaning."
            )

        clients = (
            cleaned["AccountId"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

        symbols = (
            cleaned["Symbol"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

        return MTFImportResult(
            dataframe=cleaned,
            source_file=source_file,
            records_received=len(dataframe),
            records_after_cleaning=len(cleaned),
            clients=int(clients),
            symbols=int(symbols),
        )

    @classmethod
    def _normalize_columns(
        cls,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        result = dataframe.copy()

        normalized = {}

        for column in result.columns:
            original = str(column).strip()

            lookup = original.upper()

            normalized_column = cls.COLUMN_ALIASES.get(
                lookup,
                original,
            )

            normalized[original] = normalized_column

        result = result.rename(columns=normalized)

        return result

    @classmethod
    def _clean_dataframe(
        cls,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        result = dataframe.copy()

        # Normalize text identifiers.
        for column in ("AccountId", "Symbol"):
            if column in result.columns:
                result[column] = (
                    result[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

        # Convert financial / quantity fields to numeric.
        for column in cls.NUMERIC_COLUMNS:
            if column not in result.columns:
                continue

            result[column] = pd.to_numeric(
                result[column],
                errors="coerce",
            )

        # Broker exports may leave MTM blank when the
        # position has no MTM difference. Treat blank MTM
        # as zero rather than dropping the valid position.
        if "MarkToMarket" in result.columns:
            result["MarkToMarket"] = result["MarkToMarket"].fillna(0.0)    

        # Required identifiers cannot be empty.
        result = result[
            result["AccountId"].ne("")
            & result["Symbol"].ne("")
        ].copy()

        # Required numeric fields must be usable.
        required_numeric = (
            "NetValue",
            "NetQty",
            "BUY VALUE",
            "MTF VAR",
            "MTF MARGIN",
        )

        result = result.dropna(
            subset=list(required_numeric),
        )

        result = result.reset_index(drop=True)

        return result