"""Finance Utility Suite - Unified Report Controller v1.37.2."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any
import pandas as pd
from desktop.reports.client_holdings_report import ClientHoldingsReport
from desktop.reports.portfolio_report import PortfolioReport
from desktop.reports.analytics_report import AnalyticsReport

class ReportController:
    VERSION = "1.38.1"
    DEFAULT_DIRECTORY = Path.home() / "Documents"
    @classmethod
    def _timestamp(cls) -> str: return datetime.now().strftime("%Y%m%d_%H%M%S")
    @classmethod
    def _save_dialog(cls, default_name: str) -> str | None:
        return filedialog.asksaveasfilename(title="Export Report", initialdir=str(cls.DEFAULT_DIRECTORY), initialfile=default_name, defaultextension=".xlsx", filetypes=[("Excel Workbook", "*.xlsx")])
    @staticmethod
    def _show_success(filepath: str | Path) -> None: messagebox.showinfo("Report Export", f"Report exported successfully.\n\n{filepath}")
    @staticmethod
    def _show_error(error: Exception) -> None: messagebox.showerror("Report Export", str(error))
    @classmethod
    def generate_client_holdings(cls, filepath: str | Path, *, account_id: str, holdings_df: pd.DataFrame, summary_data: dict[str, Any] | None = None) -> Path:
        return ClientHoldingsReport(account_id=account_id, holdings_df=holdings_df, summary_data=summary_data).export(filepath)
    @classmethod
    def generate_portfolio(cls, filepath: str | Path, *, portfolio_df: pd.DataFrame, summary_data: dict[str, Any] | None = None, portfolio_name: str = "Portfolio") -> Path:
        return PortfolioReport(dataframe=portfolio_df, summary_data=summary_data, portfolio_name=portfolio_name).export(filepath)
    @classmethod
    def export_client_holdings(cls, account_id: str, holdings_df: pd.DataFrame, summary_data: dict[str, Any] | None = None) -> bool:
        filepath=cls._save_dialog(f"Client_Holdings_{account_id}_{cls._timestamp()}.xlsx")
        if not filepath: return False
        try:
            output=cls.generate_client_holdings(filepath, account_id=account_id, holdings_df=holdings_df, summary_data=summary_data); cls._show_success(output); return True
        except Exception as exc: cls._show_error(exc); return False
    @classmethod
    def export_portfolio(cls, portfolio_df: pd.DataFrame, summary: dict[str, Any] | None = None, portfolio_name: str = "Portfolio") -> bool:
        safe=''.join(c if c.isalnum() or c in '-_' else '_' for c in portfolio_name.strip()) or 'Portfolio'
        filepath=cls._save_dialog(f"{safe}_Report_{cls._timestamp()}.xlsx")
        if not filepath: return False
        try:
            output=cls.generate_portfolio(filepath, portfolio_df=portfolio_df, summary_data=summary, portfolio_name=portfolio_name); cls._show_success(output); return True
        except Exception as exc: cls._show_error(exc); return False
    @classmethod
    def generate_analytics(cls, filepath: str | Path, *, portfolio_df: pd.DataFrame, summary_data: dict[str, Any] | None = None, portfolio_name: str = "Portfolio") -> Path:
        return AnalyticsReport(dataframe=portfolio_df, summary_data=summary_data, portfolio_name=portfolio_name).export(filepath)
    @classmethod
    def export_analytics(cls, portfolio_df: pd.DataFrame, summary: dict[str, Any] | None = None, portfolio_name: str = "Portfolio") -> bool:
        safe=''.join(c if c.isalnum() or c in '-_' else '_' for c in portfolio_name.strip()) or 'Portfolio'
        filepath=cls._save_dialog(f"{safe}_Analytics_{cls._timestamp()}.xlsx")
        if not filepath: return False
        try:
            output=cls.generate_analytics(filepath, portfolio_df=portfolio_df, summary_data=summary, portfolio_name=portfolio_name); cls._show_success(output); return True
        except Exception as exc: cls._show_error(exc); return False
