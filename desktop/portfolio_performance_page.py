"""
Finance Utility Suite
Portfolio Performance Dashboard

Generates equity curve, drawdown and daily P/L trend automatically
from current holdings using Yahoo Finance historical prices.

Version: 1.30 Beta
"""

from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from core.services.portfolio_performance_service import PortfolioPerformanceService
from desktop.base_page import BasePage
from desktop.widgets.chart_widget import ChartWidget
from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.result_table import ResultTable


class PortfolioPerformancePage(BasePage):
    """Portfolio Performance Dashboard."""

    def __init__(self, master):
        super().__init__(
            master,
            title="Portfolio Performance Dashboard",
        )

        self.holdings_df: pd.DataFrame | None = None
        self.performance_df: pd.DataFrame | None = None

        self.value_card: DashboardCard | None = None
        self.cagr_card: DashboardCard | None = None
        self.return_card: DashboardCard | None = None
        self.drawdown_card: DashboardCard | None = None

        self.equity_chart: ChartWidget | None = None
        self.drawdown_chart: ChartWidget | None = None
        self.daily_pnl_chart: ChartWidget | None = None

        self.result_table: ResultTable | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build dashboard UI."""

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(3, weight=1)

        self._build_toolbar()
        self._build_cards()
        self._build_charts()
        self._build_table()

    def _build_toolbar(self) -> None:
        """Build toolbar."""

        toolbar = ctk.CTkFrame(self.content)
        toolbar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(10, 10),
        )

        self.import_button = ctk.CTkButton(
            toolbar,
            text="Import Holdings",
            command=self.import_file,
        )
        self.import_button.pack(side="left", padx=10, pady=10)

        self.generate_button = ctk.CTkButton(
            toolbar,
            text="Generate Performance",
            command=self.generate_performance,
        )
        self.generate_button.pack(side="left", padx=10, pady=10)

    def _build_cards(self) -> None:
        """Build performance summary cards."""

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        for column in range(4):
            cards.grid_columnconfigure(column, weight=1)

        self.value_card = DashboardCard(
            cards,
            title="Portfolio Value",
            value="₹0.00",
            icon="💼",
        )
        self.value_card.grid(row=0, column=0, sticky="ew", padx=8)

        self.cagr_card = DashboardCard(
            cards,
            title="CAGR",
            value="0.00%",
            icon="📈",
        )
        self.cagr_card.grid(row=0, column=1, sticky="ew", padx=8)

        self.return_card = DashboardCard(
            cards,
            title="Total Return",
            value="0.00%",
            icon="📊",
        )
        self.return_card.grid(row=0, column=2, sticky="ew", padx=8)

        self.drawdown_card = DashboardCard(
            cards,
            title="Max Drawdown",
            value="0.00%",
            icon="📉",
        )
        self.drawdown_card.grid(row=0, column=3, sticky="ew", padx=8)

    def _build_charts(self) -> None:
        """Build chart layout."""

        charts = ctk.CTkFrame(self.content, fg_color="transparent")
        charts.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 12))
        charts.grid_columnconfigure(0, weight=1)
        charts.grid_columnconfigure(1, weight=1)

        self.equity_chart = ChartWidget(charts)
        self.equity_chart.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=8,
            pady=8,
        )

        self.drawdown_chart = ChartWidget(charts)
        self.drawdown_chart.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=8,
            pady=8,
        )

        self.daily_pnl_chart = ChartWidget(charts)
        self.daily_pnl_chart.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=8,
            pady=8,
        )

    def _build_table(self) -> None:
        """Build performance table."""

        self.result_table = ResultTable(self.content)
        self.result_table.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20),
        )

    def import_file(self) -> None:
        """Import current holdings file."""

        file_path = filedialog.askopenfilename(
            title="Select Holdings File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
            ],
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                self.holdings_df = pd.read_csv(file_path)
            else:
                self.holdings_df = pd.read_excel(file_path)

            self.set_status("Holdings imported. Click Generate Performance.")

        except Exception as error:
            messagebox.showerror("Import Error", str(error))

    def generate_performance(self) -> None:
        """Generate performance history from Yahoo Finance."""

        if self.holdings_df is None or self.holdings_df.empty:
            self.set_status("Please import holdings first.")
            return

        try:
            self.set_status("Downloading Yahoo Finance history...")

            dataframe, summary = PortfolioPerformanceService.generate_history(
                self.holdings_df,
                days=365,
            )

            self.performance_df = dataframe

            self._refresh_cards(summary)
            self._refresh_charts(dataframe)
            self._refresh_table(dataframe)

            self.set_status("Portfolio performance generated successfully.")

        except Exception as error:
            self.set_status("Performance generation failed.")
            messagebox.showerror("Portfolio Performance", str(error))

    def _refresh_cards(self, summary: dict) -> None:
        """Refresh dashboard cards."""

        if self.value_card is not None:
            self.value_card.set_value(f"₹{summary['end_value']:,.2f}")

        if self.cagr_card is not None:
            self.cagr_card.set_value(f"{summary['cagr']:.2f}%")

        if self.return_card is not None:
            self.return_card.set_value(f"{summary['total_return']:.2f}%")

        if self.drawdown_card is not None:
            self.drawdown_card.set_value(f"{summary['max_drawdown']:.2f}%")

    def _refresh_charts(self, dataframe: pd.DataFrame) -> None:
        """Refresh charts."""

        if dataframe is None or dataframe.empty:
            return

        chart_df = dataframe.copy()
        chart_df["Date Label"] = pd.to_datetime(chart_df["Date"]).dt.strftime("%d-%b")

        if self.equity_chart is not None:
            self.equity_chart.plot_line(
                x=chart_df["Date Label"].tolist(),
                y=chart_df["Portfolio Value"].tolist(),
                title="Equity Curve",
                xlabel="Date",
                ylabel="Portfolio Value",
            )

        if self.drawdown_chart is not None:
            self.drawdown_chart.plot_line(
                x=chart_df["Date Label"].tolist(),
                y=chart_df["Drawdown %"].tolist(),
                title="Drawdown Chart",
                xlabel="Date",
                ylabel="Drawdown %",
            )

        recent_df = chart_df.tail(30)

        if self.daily_pnl_chart is not None:
            self.daily_pnl_chart.plot_bar(
                x=recent_df["Date Label"].tolist(),
                y=recent_df["Daily P/L"].tolist(),
                title="Daily P/L Trend - Last 30 Trading Days",
                xlabel="Date",
                ylabel="Daily P/L",
            )

    def _refresh_table(self, dataframe: pd.DataFrame) -> None:
        """Refresh performance table."""

        if self.result_table is None:
            return

        display_df = dataframe.copy()
        display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.strftime("%d-%b-%Y")

        for column in ["Portfolio Value", "Daily P/L", "Peak Value"]:
            if column in display_df.columns:
                display_df[column] = display_df[column].map(
                    lambda value: f"₹{float(value):,.2f}"
                )

        for column in ["Daily Return %", "Cumulative Return %", "Drawdown %"]:
            if column in display_df.columns:
                display_df[column] = display_df[column].map(
                    lambda value: f"{float(value):.2f}%"
                )

        self.result_table.load_dataframe(display_df)
