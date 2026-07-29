"""
Finance Utility Suite
Result Table Widget

Professional reusable data table with sorting, zebra rows,
context menu, copy support, status bar and detail window.

Author : Shiva Kumar
Version: 1.01
"""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from typing import Any, Callable

import customtkinter as ctk
import pandas as pd
from tkinter import ttk

from desktop.theme import Theme
from desktop.windows.stock_details import StockDetailsWindow


class ResultTable(ctk.CTkFrame):
    """Reusable result table widget."""

    NUMERIC_KEYWORDS = (
        "price",
        "value",
        "profit",
        "loss",
        "return",
        "amount",
        "investment",
        "qty",
        "quantity",
        "beta",
        "score",
        "%",
    )

    def __init__(
        self,
        master,
        on_double_click: Callable[[dict[str, Any]], None] | None = None,
    ):
        super().__init__(
            master,
            corner_radius=Theme.BORDER_RADIUS,
            border_width=1,
        )

        self.on_double_click = on_double_click

        self.dataframe: pd.DataFrame | None = None
        self.columns: list[str] = []

        self.sort_column: str | None = None
        self.sort_reverse = False
        self.selected_item: str | None = None

        self._configure_style()
        self._build_ui()
        self._bind_events()

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    def _build_ui(self) -> None:
        """Build table UI."""

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self,
            show="headings",
            selectmode="browse",
            style="Result.Treeview",
        )

        self.tree.tag_configure("evenrow", background="#FFFFFF")
        self.tree.tag_configure("oddrow", background="#F7F7F7")
        self.tree.tag_configure("selected", background="#CFE8FF")

        self.v_scroll = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
        )

        self.h_scroll = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview,
        )

        self.tree.configure(
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            height=28,
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        )
        self.status_label.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=5,
            pady=(5, 0),
        )

        self.menu = tk.Menu(self, tearoff=False)
        self.menu.add_command(label="Copy Row", command=self._copy_row)
        self.menu.add_separator()
        self.menu.add_command(label="Open Details", command=self._open_selected)

    def _configure_style(self) -> None:
        """Configure ttk Treeview style."""

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Result.Treeview",
            rowheight=Theme.TREE_ROW_HEIGHT,
            font=Theme.FONT_NORMAL,
        )

        style.configure(
            "Result.Treeview.Heading",
            font=Theme.FONT_SMALL,
        )

    def _bind_events(self) -> None:
        """Bind table events."""

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def load_dataframe(self, dataframe: pd.DataFrame) -> None:
        """Load dataframe into table."""

        if dataframe is None or dataframe.empty:
            self.clear()
            self._update_status()
            return

        self.dataframe = dataframe.copy()
        self.columns = list(dataframe.columns)

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self.columns

        self._set_headers()
        self._configure_columns()

        for row in dataframe.itertuples(index=False):
            self.tree.insert("", "end", values=list(row))

        self._apply_zebra()
        self._update_status()

    def clear(self) -> None:
        """Clear all table rows."""

        self.tree.delete(*self.tree.get_children())
        self.columns = []
        self.tree["columns"] = []
        self.selected_item = None

    def search(self, text: str) -> None:
        """Search table by Symbol column."""

        if self.dataframe is None:
            return

        query = text.upper().strip()

        if query == "":
            self.load_dataframe(self.dataframe)
            return

        symbol_column = self._find_symbol_column()

        if symbol_column is None:
            return

        filtered = self.dataframe[
            self.dataframe[symbol_column]
            .astype(str)
            .str.upper()
            .str.contains(query, na=False)
        ]

        self._load_filtered_dataframe(filtered)

    def sort_by_column(self, column: str) -> None:
        """Sort visible table rows by selected column."""

        rows = []

        for item in self.tree.get_children():
            value = self.tree.set(item, column)
            rows.append((self._convert_value(value), item))

        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        rows.sort(key=lambda item: item[0], reverse=self.sort_reverse)

        for index, (_, item) in enumerate(rows):
            self.tree.move(item, "", index)

        self._set_headers()
        self._apply_zebra()
        self._update_status()

    # -----------------------------------------------------
    # Table Configuration
    # -----------------------------------------------------

    def _set_headers(self) -> None:
        """Set sortable column headers."""

        for column in self.columns:
            text = column

            if column == self.sort_column:
                text += " ▼" if self.sort_reverse else " ▲"

            self.tree.heading(
                column,
                text=text,
                command=lambda selected_column=column: self.sort_by_column(
                    selected_column
                ),
            )

    def _configure_columns(self) -> None:
        """Configure table column widths and alignment."""

        for column in self.columns:
            anchor = "e" if self._is_numeric_column(column) else "center"
            width = max(120, min(220, len(str(column)) * 14))

            self.tree.column(
                column,
                width=width,
                anchor=anchor,
                stretch=True,
            )

    def _load_filtered_dataframe(self, dataframe: pd.DataFrame) -> None:
        """Load filtered dataframe while preserving original data."""

        self.tree.delete(*self.tree.get_children())

        for row in dataframe.itertuples(index=False):
            self.tree.insert("", "end", values=list(row))

        self._apply_zebra()
        self._update_status()

    # -----------------------------------------------------
    # Row Styling
    # -----------------------------------------------------

    def _apply_zebra(self) -> None:
        """Apply alternating row colors."""

        for index, item in enumerate(self.tree.get_children()):
            if item == self.selected_item:
                continue

            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.item(item, tags=(tag,))

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    def _update_status(self, selected: Any | None = None) -> None:
        """Update table status bar."""

        total_rows = len(self.tree.get_children())

        message = f"Rows: {total_rows}"

        if selected is not None:
            message += f" | Selected: {selected}"

        message += f" | Updated: {datetime.now().strftime('%H:%M:%S')}"

        self.status_label.configure(text=message)

    # -----------------------------------------------------
    # Events
    # -----------------------------------------------------

    def _on_select(self, _event) -> None:
        """Handle row selection."""

        self.selected_item = self.tree.focus()

        if not self.selected_item:
            return

        values = self.tree.item(self.selected_item, "values")

        self._apply_zebra()

        if values:
            self.tree.item(self.selected_item, tags=("selected",))
            self._update_status(values[0])

    def _on_double_click(self, _event) -> None:
        """Handle row double-click."""

        item = self.tree.focus()

        if not item:
            return

        values = self.tree.item(item, "values")

        if not values:
            return

        if self.on_double_click:
            data = dict(
                zip(
                    self.columns,
                    values,
                    strict=False,
                )
            )
            self.on_double_click(data)
        else:
            self._open_detail_window(values)

    # -----------------------------------------------------
    # Detail Window
    # -----------------------------------------------------

    def _open_detail_window(self, values: Any) -> None:
        """Open stock details window."""

        if not values:
            return

        data = dict(zip(self.columns, values, strict=False))
        StockDetailsWindow(self, data)

    # -----------------------------------------------------
    # Context Menu
    # -----------------------------------------------------

    def _show_context_menu(self, event) -> None:
        """Show right-click context menu."""

        item = self.tree.identify_row(event.y)

        if not item:
            return

        self.tree.selection_set(item)
        self.tree.focus(item)
        self.selected_item = item

        self.menu.tk_popup(event.x_root, event.y_root)

    def _copy_row(self) -> None:
        """Copy selected row to clipboard."""

        if not self.selected_item:
            return

        values = self.tree.item(self.selected_item, "values")
        text = "\t".join(str(value) for value in values)

        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

        self._update_status("Row Copied")

    def _open_selected(self) -> None:
        """Open selected row details from context menu."""

        if not self.selected_item:
            return

        values = self.tree.item(self.selected_item, "values")

        if not values:
            return

        if self.on_double_click:
            data = dict(
                zip(
                    self.columns,
                    values,
                    strict=False,
                )
            )
            self.on_double_click(data)
        else:
            self._open_detail_window(values)

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def _find_symbol_column(self) -> str | None:
        """Find symbol column in dataframe."""

        if self.dataframe is None:
            return None

        for column in self.dataframe.columns:
            if str(column).upper() == "SYMBOL":
                return column

        return None

    def _is_numeric_column(self, column: str) -> bool:
        """Infer whether a column should be right-aligned."""

        column_name = str(column).lower()

        return any(keyword in column_name for keyword in self.NUMERIC_KEYWORDS)

    def _convert_value(self, value: Any) -> Any:
        """Convert value for natural sorting."""

        if value is None:
            return ""

        value = str(value).strip()
        numeric = value.replace("₹", "").replace("%", "").replace(",", "")

        try:
            return float(numeric)
        except ValueError:
            return value.upper()


    def auto_fit_columns(self) -> None:
        """Auto fit columns based on content."""
        for column in self.columns:
            width=max(120,len(column)*12)
            for item in self.tree.get_children()[:50]:
                value=str(self.tree.set(item,column))
                width=max(width,min(300,len(value)*8))
            self.tree.column(column,width=width)

    def copy_selected_cell(self)->None:
        """Copy focused cell value."""
        if not self.selected_item:
            return
        values=self.tree.item(self.selected_item,"values")
        if values:
            self.clipboard_clear()
            self.clipboard_append(str(values[0]))
            self.update()
