"""
Finance Utility Suite
Portfolio Live Dashboard

Version: 1.20
"""

from __future__ import annotations

from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from core.services.portfolio_live_service import PortfolioLiveService
from desktop.base_page import BasePage
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

        self._build_ui()

    def _build_ui(self) -> None:
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(3, weight=1)

        self._build_toolbar()
        self._build_cards()
        self._build_tables()

    def _build_toolbar(self) -> None:
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

    def _build_tables(self) -> None:
        self.result_table = ResultTable(self.content)
        self.result_table.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 12),
        )

        bottom = ctk.CTkFrame(self.content, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
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

        self.result_table.load_dataframe(display_df)
        self._refresh_summary()
        self._refresh_top_movers()
        self.start_auto_refresh()
        self.set_status("Portfolio live data updated.")

    def _refresh_summary(self) -> None:
        df = self.live_dataframe

        if df is None or df.empty:
            return

        portfolio_value = df["CURRENT_VALUE"].sum()
        pnl = df["P/L"].sum()
        invested = portfolio_value - pnl
        return_pct = (pnl / invested) * 100 if invested else 0

        self.value_card.set_value(f"₹{portfolio_value:,.2f}")
        self.pnl_card.set_value(f"₹{pnl:,.2f}")
        self.return_card.set_value(f"{return_pct:.2f}%")
        self.holdings_card.set_value(str(len(df)))

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

    def _refresh_top_movers(self) -> None:
        if self.live_dataframe is None or self.live_dataframe.empty:
            return

        df = self.live_dataframe.copy()

        gainers = df.sort_values("P/L %", ascending=False).head(5)
        losers = df.sort_values("P/L %", ascending=True).head(5)

        self.gainers_table.set_headers(["Symbol", "P/L %"])
        self.gainers_table.set_data(
            [
                [row["SYMBOL"], f"{row['P/L %']:.2f}%"]
                for _, row in gainers.iterrows()
            ]
        )

        self.losers_table.set_headers(["Symbol", "P/L %"])
        self.losers_table.set_data(
            [
                [row["SYMBOL"], f"{row['P/L %']:.2f}%"]
                for _, row in losers.iterrows()
            ]
        )

    def start_auto_refresh(self) -> None:
        if not self.auto_refresh:
            return

        self.stop_auto_refresh()

        self._refresh_job = self.after(
            self.REFRESH_INTERVAL,
            self._auto_refresh,
        )

    def stop_auto_refresh(self) -> None:
        if self._refresh_job is None:
            return

        try:
            self.after_cancel(self._refresh_job)
        except Exception:
            pass

        self._refresh_job = None

    def _auto_refresh(self) -> None:
        self._refresh_job = None
        self.refresh_portfolio()

    def toggle_auto_refresh(self) -> None:
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
        self.stop_auto_refresh()
        super().destroy()
