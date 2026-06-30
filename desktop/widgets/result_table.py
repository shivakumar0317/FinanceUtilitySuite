import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class ResultTable(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        # Store original dataframe
        self.dataframe = None

        # -----------------------------------
        # Style
        # -----------------------------------

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            rowheight=28,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

        # -----------------------------------
        # Treeview
        # -----------------------------------

        self.tree = ttk.Treeview(
            self,
            show="headings"
        )

        # Scrollbars

        y_scroll = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )

        x_scroll = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        y_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        x_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # -----------------------------------
    # Load DataFrame
    # -----------------------------------

    def load_dataframe(self, dataframe):

        # Keep original dataframe
        self.dataframe = dataframe.copy()

        # Remove old rows
        self.tree.delete(*self.tree.get_children())

        # Remove old columns
        self.tree["columns"] = list(dataframe.columns)

        # Create headings
        for column in dataframe.columns:

            self.tree.heading(
                column,
                text=column
            )

            self.tree.column(
                column,
                width=120,
                anchor="center"
            )

        # Insert rows
        for row in dataframe.itertuples(index=False):

            self.tree.insert(
                "",
                "end",
                values=list(row)
            )

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

        # Find Symbol column automatically

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

        # Draw filtered rows only

        self.tree.delete(*self.tree.get_children())

        for row in filtered.itertuples(index=False):

            self.tree.insert(
                "",
                "end",
                values=list(row)
            )