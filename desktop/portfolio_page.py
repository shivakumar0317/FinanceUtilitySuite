"""
Finance Utility Suite
Portfolio Page

Professional scrollable Portfolio Analyzer page.
Uses BasePage architecture introduced in Version 0.95.
"""

from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from core.services.portfolio_service import PortfolioService
from desktop.pages.base_page import BasePage
from desktop.widgets.chart_widget import ChartWidget
from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.mini_table import MiniTable
from desktop.widgets.performance_widget import PerformanceWidget
from desktop.widgets.result_table import ResultTable


class PortfolioPage(BasePage):
    """Portfolio Analyzer page."""

    def __init__(self, master):
        super().__init__(master)

        self.portfolio_df: pd.DataFrame | None = None

        self.total_investment: DashboardCard | None = None
        self.current_value: DashboardCard | None = None
        self.pnl: DashboardCard | None = None
        self.holdings: DashboardCard | None = None

        self.allocation_chart: ChartWidget | None = None
        self.pnl_chart: ChartWidget | None = None

        self.top_gainers_table: MiniTable | None = None
        self.top_losers_table: MiniTable | None = None

        self.performance_widget: PerformanceWidget | None = None
        self.table: ResultTable | None = None

        self.status_label: ctk.CTkLabel | None = None

        self.build_ui()

    # -----------------------------------------------------
    # UI Construction
    # -----------------------------------------------------

    def build_ui(self) -> None:
        """Build Portfolio page layout."""

        self.add_header(
            "Portfolio Analyzer",
            "Analyze holdings, allocation, returns and portfolio performance.",
        )

        self.build_toolbar()
        self.build_cards()
        self.build_charts()
        self.build_mini_tables()
        self.build_performance()
        self.build_holdings_table()

    def build_toolbar(self) -> None:
        """Build import toolbar."""

        toolbar = self.create_section(row=1, columns=2)

        import_btn = ctk.CTkButton(
            toolbar, text="📂 Import Portfolio", command=self.import_portfolio
        )
        import_btn.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(toolbar, text="Ready", anchor="w")
        self.status_label.grid(row=0, column=1, sticky="w", padx=10, pady=10)

    def build_cards(self) -> None:
        """Build summary dashboard cards."""

        cards = self.create_section(row=2, columns=4)

        self.total_investment = DashboardCard(
            cards, title="Investment", value="₹0", subtitle="Total Invested"
        )

        self.current_value = DashboardCard(
            cards, title="Current Value", value="₹0", subtitle="Market Value"
        )

        self.pnl = DashboardCard(
            cards, title="Profit / Loss", value="₹0", subtitle="Return %"
        )

        self.holdings = DashboardCard(
            cards, title="Holdings", value="0", subtitle="Total Stocks"
        )

        self.total_investment.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.current_value.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.pnl.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        self.holdings.grid(row=0, column=3, padx=8, pady=8, sticky="nsew")

    def build_charts(self) -> None:
        """Build portfolio charts section."""

        charts = self.create_section(row=3, columns=2)

        self.allocation_chart = ChartWidget(charts)
        self.allocation_chart.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.pnl_chart = ChartWidget(charts)
        self.pnl_chart.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

    def build_mini_tables(self) -> None:
        """Build Top Gainers and Top Losers tables."""

        mini_tables = self.create_section(row=4, columns=2)

        self.top_gainers_table = MiniTable(mini_tables, title="Top Gainers")
        self.top_gainers_table.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.top_losers_table = MiniTable(mini_tables, title="Top Losers")
        self.top_losers_table.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

    def build_performance(self) -> None:
        """Build portfolio performance section."""

        performance = self.create_section(row=5, columns=1)

        self.performance_widget = PerformanceWidget(
            performance, title="Portfolio Performance"
        )
        self.performance_widget.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

    def build_holdings_table(self) -> None:
        """Build holdings table section."""

        table_section = self.create_section(row=6, columns=1)

        table_section.grid_rowconfigure(0, weight=1)

        self.table = ResultTable(table_section)
        self.table.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    # -----------------------------------------------------
    # Import Workflow
    # -----------------------------------------------------

    def import_portfolio(self) -> None:
        """Import portfolio file and refresh all sections."""

        file_path = filedialog.askopenfilename(
            title="Select Portfolio",
            filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")],
        )

        if not file_path:
            return

        try:
            self.set_status("Loading portfolio...")

            dataframe, summary = PortfolioService.load(file_path)

            self.portfolio_df = dataframe

            self.update_table(dataframe)
            self.update_cards(summary)
            self.update_charts(dataframe)
            self.update_mini_tables(dataframe)
            self.update_performance(dataframe)

            self.set_status("Portfolio loaded successfully")

        except Exception as error:
            self.set_status("Import failed")
            messagebox.showerror("Portfolio Import", str(error))

    def set_status(self, message: str) -> None:
        """Update toolbar status message."""

        if self.status_label is not None:
            self.status_label.configure(text=message)

    # -----------------------------------------------------
    # Update Methods
    # -----------------------------------------------------

    def update_table(self, dataframe: pd.DataFrame) -> None:
        """Update holdings result table."""

        if self.table is not None:
            self.table.load_dataframe(dataframe)

    def update_cards(self, summary: dict) -> None:
        """Update summary cards."""

        if self.total_investment is not None:
            self.total_investment.set_value(f"₹{summary['investment']:,.2f}")

        if self.current_value is not None:
            self.current_value.set_value(f"₹{summary['current_value']:,.2f}")

        if self.pnl is not None:
            self.pnl.set_value(f"₹{summary['profit']:,.2f}")

            self.pnl.set_subtitle(f"{summary.get('return_percent', 0)}%")

        if self.holdings is not None:
            self.holdings.set_value(summary["holdings"])

    def update_charts(self, dataframe: pd.DataFrame) -> None:
        """Update portfolio charts."""

        if dataframe is None or dataframe.empty:
            return

        required_columns = ["Symbol", "Current Value", "Profit"]

        if not self.has_columns(dataframe, required_columns):
            return

        top_df = dataframe.sort_values(by="Current Value", ascending=False).head(8)

        if self.allocation_chart is not None:
            self.allocation_chart.plot_pie(
                labels=top_df["Symbol"].tolist(),
                values=top_df["Current Value"].tolist(),
                title="Portfolio Allocation",
            )

        pnl_df = dataframe.sort_values(by="Profit", ascending=False).head(10)

        if self.pnl_chart is not None:
            self.pnl_chart.plot_bar(
                x=pnl_df["Symbol"].tolist(),
                y=pnl_df["Profit"].tolist(),
                title="Top Profit / Loss",
                xlabel="Symbol",
                ylabel="Profit",
            )

    def update_mini_tables(self, dataframe: pd.DataFrame) -> None:
        """Update Top Gainers and Top Losers tables."""

        if dataframe is None or dataframe.empty:
            return

        required_columns = ["Symbol", "Current Price", "Return %"]

        if not self.has_columns(dataframe, required_columns):
            return

        gainers_df = dataframe.sort_values(by="Return %", ascending=False).head(5)

        losers_df = dataframe.sort_values(by="Return %", ascending=True).head(5)

        gainers = [
            (row["Symbol"], row["Current Price"], row["Return %"])
            for _, row in gainers_df.iterrows()
        ]

        losers = [
            (row["Symbol"], row["Current Price"], row["Return %"])
            for _, row in losers_df.iterrows()
        ]

        if self.top_gainers_table is not None:
            self.top_gainers_table.load_data(gainers)

        if self.top_losers_table is not None:
            self.top_losers_table.load_data(losers)

    def update_performance(self, dataframe: pd.DataFrame) -> None:
        """Update portfolio performance metrics."""

        if dataframe is None or dataframe.empty:
            return

        required_columns = ["Symbol", "Return %", "Profit"]

        if not self.has_columns(dataframe, required_columns):
            return

        best_row = dataframe.loc[dataframe["Return %"].idxmax()]
        worst_row = dataframe.loc[dataframe["Return %"].idxmin()]

        average_return = dataframe["Return %"].mean()
        winning_stocks = dataframe[dataframe["Return %"] > 0].shape[0]
        losing_stocks = dataframe[dataframe["Return %"] < 0].shape[0]
        total_profit = dataframe["Profit"].sum()

        metrics = {
            "Best Performer": (
                f"{best_row['Symbol']} " f"({best_row['Return %']:.2f}%)"
            ),
            "Worst Performer": (
                f"{worst_row['Symbol']} " f"({worst_row['Return %']:.2f}%)"
            ),
            "Average Return": f"{average_return:.2f}%",
            "Winning Stocks": winning_stocks,
            "Losing Stocks": losing_stocks,
            "Total Profit": f"₹{total_profit:,.2f}",
        }

        if self.performance_widget is not None:
            self.performance_widget.update_metrics(metrics)

    # -----------------------------------------------------
    # Utility Methods
    # -----------------------------------------------------

    @staticmethod
    def has_columns(dataframe: pd.DataFrame, columns: list[str]) -> bool:
        """Check whether dataframe contains required columns."""

        return all(column in dataframe.columns for column in columns)
