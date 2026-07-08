"""
Finance Utility Suite
Live Market Dashboard

Version: 1.10
"""

from __future__ import annotations

from datetime import datetime

import customtkinter as ctk

from core.services.live_market_service import LiveMarketService
from desktop.base_page import BasePage
from desktop.widgets.dashboard_card import DashboardCard
from core.services.market_status_service import MarketStatusService
from desktop.widgets.mini_table import MiniTable


class LiveMarketPage(BasePage):
    """Live Market Dashboard."""

    REFRESH_INTERVAL = 30000  # 30 seconds

    def __init__(self, master):
        super().__init__(
            master,
            title="Live Market Dashboard",
        )

        self.auto_refresh = True

        self._build_ui()
        self.refresh_market()

    def _build_ui(self) -> None:
        self.content.grid_columnconfigure(0, weight=1)

        # Toolbar
        toolbar = ctk.CTkFrame(self.content)
        toolbar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(5, 12),
        )

        self.refresh_button = ctk.CTkButton(
            toolbar,
            text="Refresh",
            command=self.refresh_market,
            width=120,
        )
        self.refresh_button.pack(
            side="right",
            padx=10,
            pady=10,
        )

        self.auto_button = ctk.CTkButton(
            toolbar,
            text="Auto Refresh: ON",
            command=self.toggle_auto_refresh,
            width=160,
        )
        self.auto_button.pack(
            side="right",
            padx=10,
            pady=10,
        )

        # Cards
        cards = ctk.CTkFrame(
            self.content,
            fg_color="transparent",
        )
        cards.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 12),
        )

        for i in range(4):
            cards.grid_columnconfigure(i, weight=1)

        self.nifty_card = DashboardCard(
            cards,
            title="NIFTY 50",
            value="-",
            icon="📈",
        )
        self.nifty_card.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8),
        )

        self.sensex_card = DashboardCard(
            cards,
            title="SENSEX",
            value="-",
            icon="📊",
        )
        self.sensex_card.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=8,
        )

        self.banknifty_card = DashboardCard(
            cards,
            title="BANKNIFTY",
            value="-",
            icon="🏦",
        )
        self.banknifty_card.grid(
            row=0,
            column=2,
            sticky="ew",
            padx=8,
        )

        self.vix_card = DashboardCard(
            cards,
            title="INDIA VIX",
            value="-",
            icon="⚠",
        )
        self.vix_card.grid(
            row=0,
            column=3,
            sticky="ew",
            padx=(8, 0),
        )

        self.last_update = ctk.CTkLabel(
            self.content,
            text="Last Updated: -",
        )
        self.last_update.grid(
            row=2,
            column=0,
            sticky="e",
            padx=20,
            pady=(0, 12),
        )

        self.market_status_card = DashboardCard(
            self.content,
            title="Market Status",
            value="Loading...",
            icon="🕒",
        )

        self.market_status_card.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 12),
        )

        tables = ctk.CTkFrame(
            self.content,
            fg_color="transparent",
        )

        tables.grid(
            row=4,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20),
        )

        tables.grid_columnconfigure(0, weight=1)
        tables.grid_columnconfigure(1, weight=1)

        self.gainers_table = MiniTable(
            tables,
            title="Top Gainers",
        )

        self.gainers_table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10),
        )

        self.losers_table = MiniTable(
            tables,
            title="Top Losers",
        )

        self.losers_table.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0),
        )

    def refresh_market(self) -> None:
        try:
            df = LiveMarketService.get_indices()

            for _, row in df.iterrows():
                name = row["Index"]
                price = f"{row['Price']:,.2f}"
                change = row["Change"]

                if name == "NIFTY 50":
                    self._update_card(self.nifty_card, price, change)
                elif name == "SENSEX":
                    self._update_card(self.sensex_card, price, change)
                elif name == "BANKNIFTY":
                    self._update_card(self.banknifty_card, price, change)
                elif name == "INDIA VIX":
                    self._update_card(self.vix_card, price, change)

            self._refresh_market_status()
            self.refresh_top_movers()

            self.last_update.configure(
                text=f"Last Updated: {datetime.now():%d-%b-%Y %I:%M:%S %p}"
            )

            self.set_status("Market data updated")

        except Exception as error:
            self.set_status(str(error))

        if self.auto_refresh:
            self.after(self.REFRESH_INTERVAL, self.refresh_market)

    def _refresh_market_status(self) -> None:
        status = MarketStatusService.get_status_text()

        self.market_status_card.set_value(status)
        self.market_status_card.set_subtitle(MarketStatusService.get_market_hours())

        if MarketStatusService.is_market_open():
            self.market_status_card.set_value_color("#16A34A")
            self.market_status_card.set_status("success")
        else:
            self.market_status_card.set_value_color("#DC2626")
            self.market_status_card.set_status("error")

    def refresh_top_movers(self) -> None:
        gainers, losers = LiveMarketService.get_top_movers()

        self.gainers_table.set_headers(["Symbol", "% Change"])
        self.gainers_table.set_data([[s, f"{c:.2f}%"] for s, c in gainers])

        self.losers_table.set_headers(["Symbol", "% Change"])
        self.losers_table.set_data([[s, f"{c:.2f}%"] for s, c in losers])

    def _update_card(self, card, value, change) -> None:
        card.set_value(value)

        if change >= 0:
            card.set_value_color("#16A34A")
        else:
            card.set_value_color("#DC2626")

    def toggle_auto_refresh(self) -> None:
        self.auto_refresh = not self.auto_refresh

        text = "Auto Refresh: ON" if self.auto_refresh else "Auto Refresh: OFF"
        self.auto_button.configure(text=text)

        if self.auto_refresh:
            self.refresh_market()