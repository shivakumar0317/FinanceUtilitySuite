"""
Finance Utility Suite
Executive Cards Widget

Displays the executive KPI cards used
throughout the Enterprise Dashboard.

Author : Shiva Kumar
Version : 2.1.0
"""

from __future__ import annotations

import customtkinter as ctk

from desktop.widgets.risk_metric_card import RiskMetricCard


class ExecutiveCards(ctk.CTkFrame):
    """
    Executive KPI cards.

    Public Methods
    --------------
    load(...)
        Populate KPI cards.

    clear()
        Reset cards.
    """

    def __init__(self, master, **kwargs):

        super().__init__(
            master,
            fg_color="transparent",
            **kwargs,
        )

        self.cards: dict[str, RiskMetricCard] = {}

        self._build()

        self.clear()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build(self):

        for column in range(3):
            self.grid_columnconfigure(column, weight=1)

        definitions = [

            ("score", "Risk Score"),

            ("health", "Portfolio Health"),

            ("exposure", "Total Exposure"),

            ("mtm", "MTM"),

            ("margin", "Margin Utilization"),

            ("diversification", "Diversification"),
        ]

        for index, (key, title) in enumerate(definitions):

            card = RiskMetricCard(
                self,
                title=title,
                value="--",
                subtitle="Waiting for portfolio...",
                height=130,
            )

            card.grid(
                row=index // 3,
                column=index % 3,
                padx=8,
                pady=8,
                sticky="nsew",
            )

            self.cards[key] = card

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def clear(self):

        for card in self.cards.values():

            card.set_data(
                "--",
                "Waiting for portfolio...",
                "Neutral",
            )

    def load(
        self,
        *,
        risk_score: float,
        health: str,
        exposure: str,
        mtm: str,
        margin: float,
        diversification: float,
    ):

        health_status = "Neutral"

        if health.lower() == "healthy":
            health_status = "Healthy"

        elif health.lower() == "moderate":
            health_status = "Warning"

        elif "high" in health.lower():
            health_status = "Critical"

        mtm_status = "Healthy"

        if mtm.startswith("-"):
            mtm_status = "Critical"

        self.cards["score"].set_data(
            f"{risk_score:.0f}",
            "Overall Risk Score",
            "Neutral",
        )

        self.cards["health"].set_data(
            health,
            "Portfolio Status",
            health_status,
        )

        self.cards["exposure"].set_data(
            exposure,
            "Current Exposure",
            "Neutral",
        )

        self.cards["mtm"].set_data(
            mtm,
            "Net Profit" if not mtm.startswith("-") else "Net Loss",
            mtm_status,
        )

        self.cards["margin"].set_data(
            f"{margin:.2f}%",
            "Margin Utilized",
            "Warning" if margin > 75 else "Healthy",
        )

        self.cards["diversification"].set_data(
            f"{diversification:.2f}%",
            "Portfolio Spread",
            "Healthy",
        )