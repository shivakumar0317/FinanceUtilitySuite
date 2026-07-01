"""
Finance Utility Suite
Mini Table Widget

Reusable widget for displaying Top Gainers,
Top Losers and other small datasets.
"""

from __future__ import annotations

import customtkinter as ctk

from tkinter import ttk


class MiniTable(ctk.CTkFrame):
    """
    Compact Treeview table.

    Used for:
        • Top Gainers
        • Top Losers
        • Watchlist
        • Recent Trades
    """

    def __init__(self, master, title: str = ""):

        super().__init__(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 15, "bold")
        )

        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=(10, 5)
        )

        # -------------------------------------------------
        # Style
        # -------------------------------------------------

        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "Mini.Treeview",
            rowheight=28,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Mini.Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

        # -------------------------------------------------
        # Treeview
        # -------------------------------------------------

        columns = (
            "symbol",
            "price",
            "change"
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=8,
            style="Mini.Treeview"
        )

        self.tree.heading("symbol", text="Symbol")
        self.tree.heading("price", text="Price")
        self.tree.heading("change", text="% Change")

        self.tree.column(
            "symbol",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "price",
            width=100,
            anchor="e"
        )

        self.tree.column(
            "change",
            width=100,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(10, 0),
            pady=(0, 10)
        )

        scrollbar.grid(
            row=1,
            column=1,
            sticky="ns",
            pady=(0, 10)
        )

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def clear(self):
        """Remove all rows."""

        for row in self.tree.get_children():
            self.tree.delete(row)

    def load_data(self, rows):
        """
        Load rows into table.

        rows example:

        [
            ("RELIANCE", 2875.50, 2.51),
            ("INFY", 1554.00, -1.24)
        ]
        """

        self.clear()

        for symbol, price, change in rows:

            self.tree.insert(
                "",
                "end",
                values=(
                    symbol,
                    f"₹{price:,.2f}",
                    f"{change:.2f}%"
                )
            )