"""
Finance Utility Suite
Mini Table Widget

Compact reusable table used for Top Gainers, Top Losers,
watchlists, risk lists, exposure summaries and small datasets.

Author : Shiva Kumar
Version: 1.00
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
        super().__init__(
            master,
            corner_radius=Theme.BORDER_RADIUS,
            border_width=1,
        )

        self.title = title
        self.columns = tuple(columns or self.DEFAULT_COLUMNS)
        self.height = height
        self.on_double_click = on_double_click

        self.tree: ttk.Treeview | None = None
        self.title_label: ctk.CTkLabel | None = None
        self.empty_label: ctk.CTkLabel | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build mini table UI."""

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.grid_propagate(False)

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
        self._create_tree()

        if self.on_double_click is not None and self.tree is not None:
            self.tree.bind("<Double-1>", self._handle_double_click)

    def _create_tree(self) -> None:
        """Create treeview using current columns."""

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
        self.tree.tag_configure("oddrow", background="#F7F7F7")
        self.tree.tag_configure("evenrow", background="#FFFFFF")

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
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.TEXT_SECONDARY,
        )

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
            font=Theme.FONT_SUBHEADING,
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

    def set_headers(self, headers: Iterable[str]) -> None:
        """Update table headers dynamically."""

        headers = list(headers)

        if self.tree is None:
            return

        self.columns = tuple(
            (
                self._normalize_column_id(header),
                header,
                self._guess_width(header),
                self._guess_anchor(header),
            )
            for header in headers
        )

        column_ids = [column[0] for column in self.columns]

        self.tree.configure(columns=column_ids)

        for column_id, heading, width, anchor in self.columns:
            self.tree.heading(column_id, text=heading)
            self.tree.column(
                column_id,
                width=width,
                anchor=anchor,
                stretch=True,
            )

    def set_data(self, rows: Iterable[Iterable]) -> None:
        """Backward-compatible method for loading data."""

        self.load_data(rows)

    def load_data(self, rows: Iterable[Iterable]) -> None:
        """Load rows into table."""

        if self.tree is None:
            return

        self.clear()

        row_count = 0

        for index, row in enumerate(rows):
            row_tuple = tuple(row)
            values = self._format_row(row_tuple)
            tags = self._get_row_tags(row_tuple, index)

            self.tree.insert(
                "",
                "end",
                values=values,
                tags=tags,
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

        return tuple(self._format_value(value) for value in row)

    def _format_value(self, value: object) -> str:
        """Format individual cell value."""

        if value is None:
            return ""

        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)

        if abs(number) >= 1000:
            return f"{number:,.2f}"

        if number % 1 == 0:
            return f"{number:,.0f}"

        return f"{number:.2f}"

    def _get_row_tags(self, row: tuple, index: int) -> tuple[str, ...]:
        """Return row styling tags."""

        zebra_tag = "evenrow" if index % 2 == 0 else "oddrow"
        value_tag = self._get_value_tag(row)

        return zebra_tag, value_tag

    def _get_value_tag(self, row: tuple) -> str:
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

    def _normalize_column_id(self, header: str) -> str:
        """Convert header text into safe treeview column id."""

        return (
            str(header)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )

    def _guess_width(self, header: str) -> int:
        """Guess column width from header name."""

        header_upper = str(header).upper()

        if "ACCOUNT" in header_upper or "CLIENT" in header_upper:
            return 140

        if "SYMBOL" in header_upper:
            return 120

        if "VALUE" in header_upper or "MARGIN" in header_upper:
            return 130

        if "MTM" in header_upper or "MARKTOMARKET" in header_upper:
            return 130

        return 110

    def _guess_anchor(self, header: str) -> str:
        """Guess alignment from header name."""

        header_upper = str(header).upper()

        numeric_words = [
            "VALUE",
            "MARGIN",
            "MTM",
            "QTY",
            "PRICE",
            "PERCENT",
            "VAR",
            "SCORE",
            "POSITIONS",
        ]

        if any(word in header_upper for word in numeric_words):
            return "e"

        return "center"

    def set_height(self, rows: int) -> None:
        """Update visible row count."""
        self.height = rows
        if self.tree is not None:
            self.tree.configure(height=rows)
