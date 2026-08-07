"""
Finance Utility Suite
Risk Summary Panel

Reusable dashboard widget that displays
the executive portfolio risk summary.

Author : Shiva Kumar
Version : 2.1.0
"""

from __future__ import annotations

import customtkinter as ctk


class RiskSummaryPanel(ctk.CTkFrame):
    """
    Dashboard widget displaying
    executive risk summary.

    Public Methods
    --------------
    load(...)
        Display risk metrics.

    clear()
        Reset all values.
    """

    def __init__(self, master, **kwargs):

        super().__init__(
            master,
            corner_radius=12,
            border_width=1,
            **kwargs,
        )

        self._labels: dict[str, ctk.CTkLabel] = {}

        self._build()

        self.clear()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build(self):

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="🛡 Risk Summary",
            font=("Segoe UI", 16, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=16,
            pady=(14, 12),
        )

        fields = [

            ("Risk Score", "risk_score"),

            ("Health", "health"),

            ("Margin Utilization", "margin"),

            ("Diversification", "diversification"),

            ("Top Client", "top_client"),

            ("Top Symbol", "top_symbol"),
        ]

        for row, (caption, key) in enumerate(fields, start=1):

            ctk.CTkLabel(
                self,
                text=caption,
                font=("Segoe UI", 11),
                anchor="w",
                text_color=("#666666", "#A0A0A0"),
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(16, 10),
                pady=6,
            )

            value = ctk.CTkLabel(
                self,
                text="--",
                font=("Segoe UI", 11, "bold"),
                anchor="w",
            )

            value.grid(
                row=row,
                column=1,
                sticky="ew",
                padx=(8, 16),
                pady=6,
            )

            self._labels[key] = value

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def clear(self):

        for label in self._labels.values():
            label.configure(text="--")

    def load(
        self,
        *,
        risk_score: float = 0.0,
        health: str = "--",
        margin_utilization: float = 0.0,
        diversification: float = 0.0,
        top_client: float = 0.0,
        top_symbol: float = 0.0,
    ):

        self._labels["risk_score"].configure(
            text=f"{risk_score:.2f}"
        )

        self._labels["health"].configure(
            text=health
        )

        self._labels["margin"].configure(
            text=f"{margin_utilization:.2f}%"
        )

        self._labels["diversification"].configure(
            text=f"{diversification:.2f}%"
        )

        self._labels["top_client"].configure(
            text=f"{top_client:.2f}%"
        )

        self._labels["top_symbol"].configure(
            text=f"{top_symbol:.2f}%"
        )