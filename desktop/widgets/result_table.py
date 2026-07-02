import tkinter as tk
from tkinter import ttk
from datetime import datetime
from desktop.windows.stock_details import StockDetailsWindow

import customtkinter as ctk


class ResultTable(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        # -----------------------------
        # Data
        # -----------------------------

        self.dataframe = None
        self.columns = []

        self.sort_column = None
        self.sort_reverse = False

        self.selected_item = None

        # -----------------------------
        # Treeview Style
        # -----------------------------

        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))

        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # -----------------------------
        # Main Treeview
        # -----------------------------

        self.tree = ttk.Treeview(self, show="headings", selectmode="browse")

        # -----------------------------
        # Row Tags
        # -----------------------------

        self.tree.tag_configure("evenrow", background="#FFFFFF")

        self.tree.tag_configure("oddrow", background="#F7F7F7")

        self.tree.tag_configure("selected", background="#CFE8FF")

        # -----------------------------
        # Scrollbars
        # -----------------------------

        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)

        self.h_scroll = ttk.Scrollbar(
            self, orient="horizontal", command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set
        )

        # -----------------------------
        # Layout
        # -----------------------------

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.h_scroll.grid(row=1, column=0, sticky="ew")

        # -----------------------------
        # Status Bar
        # -----------------------------

        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w", height=28)

        self.status_label.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0)
        )

        # -----------------------------
        # Grid Weights
        # -----------------------------

        self.grid_rowconfigure(0, weight=1)

        self.grid_columnconfigure(0, weight=1)

        # -----------------------------
        # Context Menu
        # -----------------------------

        self.menu = tk.Menu(self, tearoff=False)

        self.menu.add_command(label="Copy Row", command=self._copy_row)

        self.menu.add_separator()

        self.menu.add_command(label="Open Details", command=self._open_selected)

        # -----------------------------
        # Events
        # -----------------------------

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.tree.bind("<Double-1>", self._on_double_click)

        self.tree.bind("<Button-3>", self._show_context_menu)

    # -----------------------------------
    # Load DataFrame
    # -----------------------------------

    def load_dataframe(self, dataframe):

        self.dataframe = dataframe.copy()

        self.tree.delete(*self.tree.get_children())

        self.columns = list(dataframe.columns)
        self.tree["columns"] = self.columns

        self._set_headers()

        for column in self.columns:

            self.tree.column(column, width=120, anchor="center", stretch=True)

        for row in dataframe.itertuples(index=False):

            self.tree.insert("", "end", values=list(row))

        self._apply_zebra()
        self._update_status()

    # -----------------------------------
    # Search
    # -----------------------------------

    def search(self, text):

        if self.dataframe is None:
            return

        text = text.upper().strip()

        if text == "":
            self.load_dataframe(self.dataframe)
            return

        symbol_column = None

        for column in self.dataframe.columns:

            if column.upper() == "SYMBOL":
                symbol_column = column
                break

        if symbol_column is None:
            return

        filtered = self.dataframe[
            self.dataframe[symbol_column]
            .astype(str)
            .str.upper()
            .str.contains(text, na=False)
        ]

        self.tree.delete(*self.tree.get_children())

        for row in filtered.itertuples(index=False):

            self.tree.insert("", "end", values=list(row))

        self._apply_zebra()
        self._update_status()

    # -----------------------------------
    # Sort
    # -----------------------------------

    def sort_by_column(self, column):

        data = []

        for item in self.tree.get_children():

            value = self.tree.set(item, column)

            data.append((self._convert_value(value), item))

        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        data.sort(key=lambda x: x[0], reverse=self.sort_reverse)

        for index, (_, item) in enumerate(data):

            self.tree.move(item, "", index)

        self._set_headers()
        self._apply_zebra()
        self._update_status()

    # -----------------------------------
    # Column Headers
    # -----------------------------------

    def _set_headers(self):

        for column in self.columns:

            text = column

            if column == self.sort_column:

                if self.sort_reverse:
                    text += " ▼"
                else:
                    text += " ▲"

            self.tree.heading(
                column, text=text, command=lambda c=column: self.sort_by_column(c)
            )

    # -----------------------------------
    # Zebra Striping
    # -----------------------------------

    def _apply_zebra(self):

        for index, item in enumerate(self.tree.get_children()):

            if item == self.selected_item:
                continue

            if index % 2 == 0:
                self.tree.item(item, tags=("evenrow",))
            else:
                self.tree.item(item, tags=("oddrow",))

    # -----------------------------------
    # Status Bar
    # -----------------------------------

    def _update_status(self, selected=None):

        total_rows = len(self.tree.get_children())

        message = f"Rows: {total_rows}"

        if selected:
            message += f" | Selected: {selected}"

        message += f" | Updated: " f"{datetime.now().strftime('%H:%M:%S')}"

        self.status_label.configure(text=message)

    # -----------------------------------
    # Tree Events
    # -----------------------------------

    def _on_select(self, event):

        self.selected_item = self.tree.focus()

        if not self.selected_item:
            return

        values = self.tree.item(self.selected_item, "values")

        self._apply_zebra()

        if values:
            self.tree.item(self.selected_item, tags=("selected",))

            self._update_status(values[0])

    def _on_double_click(self, event):

        item = self.tree.focus()

        if not item:
            return

        values = self.tree.item(item, "values")

        self._open_detail_window(values)

    # -----------------------------------
    # Detail Window
    # -----------------------------------

    def _open_detail_window(self, values):

        if not values:
            return

        data = {}

        for column, value in zip(self.columns, values):
            data[column] = value

        StockDetailsWindow(self, data)

    # -----------------------------------
    # Context Menu
    # -----------------------------------

    def _show_context_menu(self, event):

        item = self.tree.identify_row(event.y)

        if not item:
            return

        self.tree.selection_set(item)
        self.tree.focus(item)

        self.selected_item = item

        self.menu.tk_popup(event.x_root, event.y_root)

    def _copy_row(self):

        if not self.selected_item:
            return

        values = self.tree.item(self.selected_item, "values")

        text = "\t".join(str(v) for v in values)

        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

        self._update_status("Row Copied")

    def _open_selected(self):

        if not self.selected_item:
            return

        values = self.tree.item(self.selected_item, "values")

        self._open_detail_window(values)

    # -----------------------------------
    # Helpers
    # -----------------------------------

    def _convert_value(self, value):

        if value is None:
            return ""

        value = str(value).strip()

        numeric = value.replace("₹", "").replace("%", "").replace(",", "")

        try:
            return float(numeric)
        except ValueError:
            return value.upper()
