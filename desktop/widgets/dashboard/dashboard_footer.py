"""
Finance Utility Suite
Dashboard Footer Widget

Displays application status information
at the bottom of the Enterprise Dashboard.

Author : Shiva Kumar
Version : 2.1.0
"""

from __future__ import annotations

import customtkinter as ctk


class DashboardFooter(ctk.CTkFrame):
    """
    Enterprise Dashboard footer.

    Public Methods
    --------------
    load(...)
        Display footer information.

    clear()
        Reset footer.
    """

    def __init__(self, master, **kwargs):

        super().__init__(
            master,
            corner_radius=10,
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

        for column in range(4):
            self.grid_columnconfigure(column, weight=1)

        sections = [

            ("snapshot", "Snapshot"),

            ("refresh", "Last Refresh"),

            ("portfolio", "Portfolio"),

            ("engine", "Risk Engine"),
        ]

        for column, (key, title) in enumerate(sections):

            frame = ctk.CTkFrame(
                self,
                fg_color="transparent",
            )

            frame.grid(
                row=0,
                column=column,
                padx=12,
                pady=10,
                sticky="ew",
            )

            ctk.CTkLabel(
                frame,
                text=title,
                font=("Segoe UI", 10),
                text_color=("#666666", "#A0A0A0"),
            ).pack(anchor="w")

            value = ctk.CTkLabel(
                frame,
                text="--",
                font=("Segoe UI", 11, "bold"),
            )

            value.pack(anchor="w")

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
        snapshot: str,
        refresh: str,
        portfolio: str,
        engine: str,
    ):

        self._labels["snapshot"].configure(
            text=snapshot,
        )

        self._labels["refresh"].configure(
            text=refresh,
        )

        self._labels["portfolio"].configure(
            text=portfolio,
        )

        self._labels["engine"].configure(
            text=engine,
        )