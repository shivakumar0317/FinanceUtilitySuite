from __future__ import annotations

import re
import pandas as pd

from core.models.master_portfolio import MasterPortfolioDefaults


class DataCleaner:
    TEXT_COLUMNS = (
        "AccountId", "Exchg-Seg", "Symbol", "Instrument Name",
        "Product Type", "Series/Expiry", "Pledge Status",
    )

    NUMERIC_COLUMNS = (
        "NetQty", "NetBuyQty", "NetSellQty", "LastTradedPrice",
        "BuyAvgPrice", "BUY VALUE", "SELL VALUE", "CarryForward",
        "NetValue", "MarkToMarket", "MTF VAR", "MTF MARGIN",
        "Ledger Balance", "Exposure", "Position Ageing",
    )

    OPTIONAL_DEFAULT_COLUMNS = {
        "Company Name": MasterPortfolioDefaults.COMPANY_NAME,
        "Sector": MasterPortfolioDefaults.SECTOR,
        "Industry": MasterPortfolioDefaults.INDUSTRY,
        "Market Cap": MasterPortfolioDefaults.MARKET_CAP,
        "Scrip Category": MasterPortfolioDefaults.SCRIP_CATEGORY,
        "Beta": MasterPortfolioDefaults.BETA,
    }

    COLUMN_ALIASES = {
        "account id": "AccountId", "accountid": "AccountId",
        "client id": "AccountId", "clientid": "AccountId",
        "symbol": "Symbol", "net qty": "NetQty", "netqty": "NetQty",
        "net buy qty": "NetBuyQty", "netbuyqty": "NetBuyQty",
        "net sell qty": "NetSellQty", "netsellqty": "NetSellQty",
        "last traded price": "LastTradedPrice",
        "lasttradedprice": "LastTradedPrice", "ltp": "LastTradedPrice",
        "buy avg price": "BuyAvgPrice", "buyavgprice": "BuyAvgPrice",
        "average buy price": "BuyAvgPrice",
        "buy value": "BUY VALUE", "sell value": "SELL VALUE",
        "net value": "NetValue", "netvalue": "NetValue",
        "mark to market": "MarkToMarket", "marktomarket": "MarkToMarket",
        "mtm": "MarkToMarket", "mtf var": "MTF VAR",
        "mtf margin": "MTF MARGIN", "ledger balance": "Ledger Balance",
        "pledge status": "Pledge Status",
        "position ageing": "Position Ageing",
        "exposure": "Exposure", "total exposure": "Exposure",
        "gross exposure": "Exposure", "exposure value": "Exposure",
    }

    @classmethod
    def clean_master_portfolio(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        cleaned = dataframe.copy()
        cleaned.columns = cls._normalize_column_names(cleaned.columns)
        cleaned = cleaned.dropna(how="all").copy()

        for column in cls.TEXT_COLUMNS:
            if column in cleaned.columns:
                cleaned[column] = cleaned[column].fillna("").astype(str).str.strip()

        if "AccountId" in cleaned.columns:
            cleaned["AccountId"] = cleaned["AccountId"].str.replace(r"\.0$", "", regex=True).str.upper()

        if "Symbol" in cleaned.columns:
            cleaned["Symbol"] = (
                cleaned["Symbol"].str.upper().str.replace(r"\s+", "", regex=True)
                .str.replace(".NS", "", regex=False)
                .str.replace(".BO", "", regex=False)
            )

        cleaned = cleaned[
            cleaned["AccountId"].ne("") & cleaned["Symbol"].ne("")
        ].copy()

        for column in cls.NUMERIC_COLUMNS:
            if column in cleaned.columns:
                cleaned[column] = cls._to_numeric(cleaned[column])

        if "Exposure" not in cleaned.columns:
            cleaned["Exposure"] = pd.to_numeric(
                cleaned.get("NetValue", 0.0), errors="coerce"
            ).fillna(0.0).abs()

        for column in ("LastTradedPrice", "BuyAvgPrice", "NetBuyQty", "NetSellQty"):
            if column not in cleaned.columns:
                cleaned[column] = 0.0

        for column, default in cls.OPTIONAL_DEFAULT_COLUMNS.items():
            if column not in cleaned.columns:
                cleaned[column] = default
            else:
                cleaned[column] = cleaned[column].fillna(default)

        cleaned = cls._add_calculated_columns(cleaned)
        return cleaned.drop_duplicates().reset_index(drop=True)

    @classmethod
    def _normalize_column_names(cls, columns) -> list[str]:
        result = []
        for column in columns:
            name = re.sub(r"\s+", " ", str(column).strip())
            result.append(cls.COLUMN_ALIASES.get(name.lower(), name))
        return result

    @staticmethod
    def _to_numeric(series: pd.Series) -> pd.Series:
        cleaned = (
            series.astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
            .str.strip()
        )
        return pd.to_numeric(cleaned, errors="coerce").fillna(0.0)

    @staticmethod
    def _add_calculated_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
        result = dataframe.copy()
        qty = pd.to_numeric(result.get("NetQty", 0.0), errors="coerce").fillna(0.0)
        buy = pd.to_numeric(result.get("BUY VALUE", 0.0), errors="coerce").fillna(0.0)
        net = pd.to_numeric(result.get("NetValue", 0.0), errors="coerce").fillna(0.0)
        mtm = pd.to_numeric(result.get("MarkToMarket", 0.0), errors="coerce").fillna(0.0)
        ltp = pd.to_numeric(result.get("LastTradedPrice", 0.0), errors="coerce").fillna(0.0)

        result["Current Value"] = net.abs()
        result["Profit/Loss"] = mtm
        calc_price = result["Current Value"].div(qty.abs().where(qty.ne(0))).fillna(0.0)
        result["Current Price"] = ltp.where(ltp.gt(0), calc_price)
        result["Return %"] = (
            result["Profit/Loss"].div(buy.abs().where(buy.abs().ne(0))).mul(100).fillna(0.0)
        )

        total = float(result["Current Value"].sum())
        result["Allocation %"] = (
            result["Current Value"].div(total).mul(100) if total > 0 else 0.0
        )
        result["Risk %"] = (
            result["Allocation %"]
            * pd.to_numeric(result["Beta"], errors="coerce").fillna(1.0)
        )
        return result
