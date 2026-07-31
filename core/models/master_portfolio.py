"""
Risk Management System
Master Portfolio Data Model

Defines the standard column structure used throughout RMS.

Author  : Shiva Kumar
Version : 2.0
"""

from __future__ import annotations


class MasterPortfolioColumns:
    """Canonical column names used by the RMS master portfolio dataset."""

    ACCOUNT_ID = "AccountId"
    SYMBOL = "Symbol"
    INSTRUMENT_NAME = "Instrument Name"
    PRODUCT_TYPE = "Product Type"

    QUANTITY = "NetQty"
    BUY_VALUE = "BUY VALUE"
    SELL_VALUE = "SELL VALUE"
    NET_VALUE = "NetValue"

    CURRENT_PRICE = "Current Price"
    CURRENT_VALUE = "Current Value"

    MARK_TO_MARKET = "MarkToMarket"
    MTF_VAR = "MTF VAR"
    MTF_MARGIN = "MTF MARGIN"

    LEDGER_BALANCE = "Ledger Balance"
    EXPOSURE = "Exposure"
    PLEDGE_STATUS = "Pledge Status"

    COMPANY_NAME = "Company Name"
    SECTOR = "Sector"
    INDUSTRY = "Industry"
    MARKET_CAP = "Market Cap"
    SCRIP_CATEGORY = "Scrip Category"
    BETA = "Beta"

    PROFIT_LOSS = "Profit/Loss"
    RETURN_PERCENT = "Return %"
    ALLOCATION_PERCENT = "Allocation %"
    RISK_PERCENT = "Risk %"


class MasterPortfolioDefaults:
    """Default values used when optional data is unavailable."""

    COMPANY_NAME = ""
    SECTOR = "Unclassified"
    INDUSTRY = "Unclassified"
    MARKET_CAP = 0.0
    SCRIP_CATEGORY = "Unclassified"
    BETA = 1.0