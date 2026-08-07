"""
Finance Utility Suite
Historical Summary Card

Version : 2.2.0
"""

from __future__ import annotations

import customtkinter as ctk


class HistorySummaryCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        title: str,
        value: str,
        width: int = 240,
        height: int = 110,
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            corner_radius=12,
        )

        self.grid_propagate(False)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(
            self,
            text=title,
            anchor="w",
            font=ctk.CTkFont(size=14),
        )

        title_lbl.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(15, 0),
        )

        self.value_lbl = ctk.CTkLabel(
            self,
            text=value,
            anchor="w",
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )

        self.value_lbl.grid(
            row=1,
            column=0,
            sticky="sw",
            padx=18,
            pady=(0, 15),
        )

    def update_value(self, value):

        self.value_lbl.configure(text=value)