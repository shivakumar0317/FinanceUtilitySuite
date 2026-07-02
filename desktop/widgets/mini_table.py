"""
Finance Utility Suite
Mini Table Widget

Compact reusable table used for Top Gainers, Top Losers,
watchlists, risk lists, exposure summaries and small datasets.

Author : Shiva Kumar
Version: 0.95
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from tkinter import ttk

import customtkinter as ctk

from desktop.theme import Theme


class MiniTable(ctk.CTkFrame):
    """Reusable compact table widget."""

    DEFAULT_COLUMNS = (
        ("symbol", "Symbol", 120, "center"),
        ("price", "Price", 100, "e"),
        ("change", "% Change", 100, "center"),
    )

    def __init__(
        self,
        master,
        title: str = "",
        columns: Iterable[tuple[str, str, int, str]] | None = None,
        height: int = 8,
        on_double_click: Callable | None = None,
    ):
        super().__init__(master, corner_radius=Theme.BORDER_RADIUS)

        self.title = title
        self.columns = tuple(columns or self.DEFAULT_COLUMNS)
        self.height = height
        self.on_double_click = on_double_click

        self.tree: ttk.Treeview | None = None
        self.title_label: ctk.CTkLabel | None = None
        self.empty_label: ctk.CTkLabel | None = None

        self._build_ui()

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    def _build_ui(self) -> None:
        """Build mini table UI."""

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=Theme.FONT_SUBHEADING,
            anchor="w",
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=Theme.CARD_PADDING + 6,
            pady=(Theme.CARD_PADDING + 6, 4),
        )

        self._configure_style()

        column_ids = [column[0] for column in self.columns]

        self.tree = ttk.Treeview(
            self,
            columns=column_ids,
            show="headings",
            height=self.height,
            style="Mini.Treeview",
        )

        for column_id, heading, width, anchor in self.columns:
            self.tree.heading(column_id, text=heading)
            self.tree.column(
                column_id,
                width=width,
                anchor=anchor,
                stretch=True,
            )

        self.tree.tag_configure("positive", foreground=Theme.SUCCESS)
        self.tree.tag_configure("negative", foreground=Theme.ERROR)
        self.tree.tag_configure("neutral", foreground=Theme.TEXT_SECONDARY)

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(Theme.CARD_PADDING + 6, 0),
            pady=(0, Theme.CARD_PADDING + 6),
        )

        scrollbar.grid(
            row=1,
            column=1,
            sticky="ns",
            pady=(0, Theme.CARD_PADDING + 6),
        )

        self.empty_label = ctk.CTkLabel(
            self,
            text="No data available",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        )

        if self.on_double_click is not None:
            self.tree.bind("<Double-1>", self._handle_double_click)

    def _configure_style(self) -> None:
        """Configure ttk Treeview style."""

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Mini.Treeview",
            rowheight=Theme.TREE_ROW_HEIGHT,
            font=Theme.FONT_NORMAL,
        )

        style.configure(
            "Mini.Treeview.Heading",
            font=Theme.FONT_SMALL,
        )

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def clear(self) -> None:
        """Remove all rows from table."""

        if self.tree is None:
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

    def load_data(self, rows: Iterable[tuple]) -> None:
        """
        Load rows into table.

        Example
        -------
        [
            ("RELIANCE", 2875.50, 2.51),
            ("INFY", 1554.00, -1.24),
        ]
        """

        if self.tree is None:
            return

        self.clear()

        row_count = 0

        for row in rows:
            values = self._format_row(row)
            tag = self._get_row_tag(row)

            self.tree.insert(
                "",
                "end",
                values=values,
                tags=(tag,),
            )

            row_count += 1

        self._toggle_empty_state(row_count == 0)

    def set_title(self, title: str) -> None:
        """Update table title."""

        self.title = title

        if self.title_label is not None:
            self.title_label.configure(text=title)

    # -----------------------------------------------------
    # Private Helpers
    # -----------------------------------------------------

    def _format_row(self, row: tuple) -> tuple:
        """Format row values for display."""

        if len(row) == 3:
            symbol, price, change = row

            return (
                symbol,
                f"₹{float(price):,.2f}",
                f"{float(change):.2f}%",
            )

        return tuple(str(value) for value in row)

    def _get_row_tag(self, row: tuple) -> str:
        """Return row color tag based on final numeric value."""

        if not row:
            return "neutral"

        try:
            value = float(row[-1])
        except (TypeError, ValueError):
            return "neutral"

        if value > 0:
            return "positive"

        if value < 0:
            return "negative"

        return "neutral"

    def _toggle_empty_state(self, show: bool) -> None:
        """Show or hide empty-state label."""

        if self.empty_label is None:
            return

        if show:
            self.empty_label.grid(
                row=1,
                column=0,
                sticky="nsew",
                padx=Theme.CARD_PADDING + 6,
                pady=(0, Theme.CARD_PADDING + 6),
            )
        else:
            self.empty_label.grid_forget()

    def _handle_double_click(self, _event) -> None:
        """Handle row double-click callback."""

        if self.tree is None or self.on_double_click is None:
            return

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.on_double_click(values)
