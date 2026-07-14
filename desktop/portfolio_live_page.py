"""
Finance Utility Suite
Portfolio Live Dashboard

Version: 1.30

Adds live portfolio charts:
- Live Portfolio Allocation Pie Chart
- Live Profit / Loss Bar Chart
- Top Holdings Chart
"""

from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from core.services.portfolio_live_service import PortfolioLiveService
from desktop.base_page import BasePage
from desktop.widgets.chart_widget import ChartWidget
from desktop.widgets.dashboard_card import DashboardCard
from desktop.widgets.mini_table import MiniTable
from desktop.widgets.result_table import ResultTable


class PortfolioLivePage(BasePage):
    """Portfolio Live Dashboard."""

    REFRESH_INTERVAL = 30000

    def __init__(self, master):
        super().__init__(
            master,
            title="Portfolio Live Dashboard",
        )

        self.dataframe: pd.DataFrame | None = None
        self.live_dataframe: pd.DataFrame | None = None
        self.auto_refresh = True
        self._refresh_job: str | None = None

        self.value_card: DashboardCard | None = None
        self.pnl_card: DashboardCard | None = None
        self.return_card: DashboardCard | None = None
        self.holdings_card: DashboardCard | None = None

        self.allocation_chart: ChartWidget | None = None
        self.pnl_chart: ChartWidget | None = None
        self.top_holdings_chart: ChartWidget | None = None

        self.result_table: ResultTable | None = None
        self.gainers_table: MiniTable | None = None
        self.losers_table: MiniTable | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build page layout."""

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(3, weight=1)

        self._build_toolbar()
        self._build_cards()
        self._build_charts()
        self._build_tables()

    def _build_toolbar(self) -> None:
        """Build top action toolbar."""

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
            text="Import Portfolio",
            command=self.import_file,
        )
        self.import_button.pack(side="left", padx=10, pady=10)

        self.refresh_button = ctk.CTkButton(
            toolbar,
            text="Refresh",
            command=self.refresh_portfolio,
        )
        self.refresh_button.pack(side="left", padx=10, pady=10)

        self.auto_button = ctk.CTkButton(
            toolbar,
            text="Auto Refresh: ON",
            command=self.toggle_auto_refresh,
        )
        self.auto_button.pack(side="left", padx=10, pady=10)

    def _build_cards(self) -> None:
        """Build dashboard summary cards."""

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

        self.pnl_card = DashboardCard(
            cards,
            title="Total P/L",
            value="₹0.00",
            icon="📈",
        )
        self.pnl_card.grid(row=0, column=1, sticky="ew", padx=8)

        self.return_card = DashboardCard(
            cards,
            title="Return %",
            value="0.00%",
            icon="📊",
        )
        self.return_card.grid(row=0, column=2, sticky="ew", padx=8)

        self.holdings_card = DashboardCard(
            cards,
            title="Holdings",
            value="0",
            icon="📁",
        )
        self.holdings_card.grid(row=0, column=3, sticky="ew", padx=8)

    def _build_charts(self) -> None:
        """Build live portfolio charts."""

        charts = ctk.CTkFrame(self.content, fg_color="transparent")
        charts.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 12),
        )

        charts.grid_columnconfigure(0, weight=1)
        charts.grid_columnconfigure(1, weight=1)
        charts.grid_rowconfigure(0, weight=1)
        charts.grid_rowconfigure(1, weight=1)

        self.allocation_chart = ChartWidget(charts)
        self.allocation_chart.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
            pady=(0, 8),
        )

        self.pnl_chart = ChartWidget(charts)
        self.pnl_chart.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0),
            pady=(0, 8),
        )

        self.top_holdings_chart = ChartWidget(charts)
        self.top_holdings_chart.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=0,
            pady=(8, 0),
        )

    def _build_tables(self) -> None:
        """Build live holdings table and top movers tables."""

        self.result_table = ResultTable(self.content)
        self.result_table.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 12),
        )

        bottom = ctk.CTkFrame(self.content, fg_color="transparent")
        bottom.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)

        self.gainers_table = MiniTable(bottom, title="Top Gainers")
        self.gainers_table.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10),
        )

        self.losers_table = MiniTable(bottom, title="Top Losers")
        self.losers_table.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(10, 0),
        )

    def import_file(self) -> None:
        """Import portfolio file and refresh live dashboard."""

        file_path = filedialog.askopenfilename(
            title="Select Portfolio File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv"),
            ],
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                self.dataframe = pd.read_csv(file_path)
            else:
                self.dataframe = pd.read_excel(file_path)

            self.refresh_portfolio()

        except Exception as error:
            messagebox.showerror("Import Error", str(error))

    def refresh_portfolio(self) -> None:
        """Refresh prices, summary, charts, table and top movers."""

        if self.dataframe is None:
            self.set_status("Please import a portfolio file first.")
            return

        self.live_dataframe = PortfolioLiveService.refresh_prices(self.dataframe)

        display_df = self.live_dataframe.copy()

        for column in ["LTP", "CURRENT_VALUE", "P/L"]:
            if column in display_df.columns:
                display_df[column] = display_df[column].map(
                    lambda value: f"₹{float(value):,.2f}"
                )

        if "P/L %" in display_df.columns:
            display_df["P/L %"] = display_df["P/L %"].map(
                lambda value: f"{float(value):,.2f}%"
            )

        if self.result_table is not None:
            self.result_table.load_dataframe(display_df)

        self._refresh_summary()
        self._refresh_charts()
        self._refresh_top_movers()
        self.start_auto_refresh()
        self.set_status("Portfolio live data updated.")

    def _refresh_summary(self) -> None:
        """Refresh dashboard summary cards."""

        df = self.live_dataframe

        if df is None or df.empty:
            return

        portfolio_value = df["CURRENT_VALUE"].sum()
        pnl = df["P/L"].sum()
        invested = portfolio_value - pnl
        return_pct = (pnl / invested) * 100 if invested else 0

        if self.value_card is not None:
            self.value_card.set_value(f"₹{portfolio_value:,.2f}")

        if self.pnl_card is not None:
            self.pnl_card.set_value(f"₹{pnl:,.2f}")

        if self.return_card is not None:
            self.return_card.set_value(f"{return_pct:.2f}%")

        if self.holdings_card is not None:
            self.holdings_card.set_value(str(len(df)))

        if self.pnl_card is None or self.return_card is None:
            return

        if pnl >= 0:
            self.pnl_card.set_value_color("#16A34A")
            self.pnl_card.set_status("success")
            self.return_card.set_value_color("#16A34A")
            self.return_card.set_status("success")
        else:
            self.pnl_card.set_value_color("#DC2626")
            self.pnl_card.set_status("error")
            self.return_card.set_value_color("#DC2626")
            self.return_card.set_status("error")

    def _refresh_charts(self) -> None:
        """Refresh live allocation, P/L and top holdings charts."""

        df = self.live_dataframe

        if df is None or df.empty:
            return

        required_columns = ["SYMBOL", "CURRENT_VALUE", "P/L"]

        if not all(column in df.columns for column in required_columns):
            return

        allocation_df = df.sort_values(
            by="CURRENT_VALUE",
            ascending=False,
        ).head(8)

        if self.allocation_chart is not None:
            self.allocation_chart.plot_pie(
                labels=allocation_df["SYMBOL"].tolist(),
                values=allocation_df["CURRENT_VALUE"].tolist(),
                title="Live Portfolio Allocation",
            )

        pnl_df = df.sort_values(
            by="P/L",
            ascending=False,
        ).head(10)

        if self.pnl_chart is not None:
            self.pnl_chart.plot_bar(
                x=pnl_df["SYMBOL"].tolist(),
                y=pnl_df["P/L"].tolist(),
                title="Live Profit / Loss",
                xlabel="Symbol",
                ylabel="Profit",
            )

        holdings_df = df.sort_values(
            by="CURRENT_VALUE",
            ascending=False,
        ).head(10)

        if self.top_holdings_chart is not None:
            self.top_holdings_chart.plot_bar(
                x=holdings_df["SYMBOL"].tolist(),
                y=holdings_df["CURRENT_VALUE"].tolist(),
                title="Top Holdings",
                xlabel="Stock",
                ylabel="Current Value",
            )

    def _refresh_top_movers(self) -> None:
        """Refresh top gainers and top losers tables."""

        if self.live_dataframe is None or self.live_dataframe.empty:
            return

        df = self.live_dataframe.copy()

        if "P/L %" not in df.columns or "SYMBOL" not in df.columns:
            return

        gainers = df.sort_values("P/L %", ascending=False).head(5)
        losers = df.sort_values("P/L %", ascending=True).head(5)

        if self.gainers_table is not None:
            self.gainers_table.set_headers(["Symbol", "P/L %"])
            self.gainers_table.set_data(
                [
                    [row["SYMBOL"], f"{row['P/L %']:.2f}%"]
                    for _, row in gainers.iterrows()
                ]
            )

        if self.losers_table is not None:
            self.losers_table.set_headers(["Symbol", "P/L %"])
            self.losers_table.set_data(
                [
                    [row["SYMBOL"], f"{row['P/L %']:.2f}%"]
                    for _, row in losers.iterrows()
                ]
            )

    def start_auto_refresh(self) -> None:
        """Start auto refresh timer."""

        if not self.auto_refresh:
            return

        self.stop_auto_refresh()

        self._refresh_job = self.after(
            self.REFRESH_INTERVAL,
            self._auto_refresh,
        )

    def stop_auto_refresh(self) -> None:
        """Stop auto refresh timer."""

        if self._refresh_job is None:
            return

        try:
            self.after_cancel(self._refresh_job)
        except Exception:
            pass

        self._refresh_job = None

    def _auto_refresh(self) -> None:
        """Auto refresh callback."""

        self._refresh_job = None
        self.refresh_portfolio()

    def toggle_auto_refresh(self) -> None:
        """Enable or disable auto refresh."""

        self.auto_refresh = not self.auto_refresh

        if self.auto_refresh:
            self.auto_button.configure(text="Auto Refresh: ON")
            self.start_auto_refresh()
            self.set_status("Auto refresh enabled.")
        else:
            self.stop_auto_refresh()
            self.auto_button.configure(text="Auto Refresh: OFF")
            self.set_status("Auto refresh disabled.")

    def destroy(self) -> None:
        """Cleanly destroy page and cancel refresh job."""

        self.stop_auto_refresh()
        super().destroy()
