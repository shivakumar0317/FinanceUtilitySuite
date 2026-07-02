"""
Finance Utility Suite
Base Page

Reusable base class for all desktop pages.
Provides a scrollable content area and common layout helpers.
"""

from __future__ import annotations

import customtkinter as ctk


class BasePage(ctk.CTkFrame):
    """
    Base class for application pages.

    Features:
        - Scrollable content area
        - Standard padding
        - Responsive grid layout
        - Common page header helper
    """

    PAGE_PAD_X = 20
    PAGE_PAD_Y = 20
    SECTION_PAD_Y = 10

    def __init__(self, master):
        super().__init__(master)

        self.content = None

        self._build_base_layout()

    def _build_base_layout(self):
        """Create the scrollable page container."""

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.content = ctk.CTkScrollableFrame(self)
        self.content.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.content.grid_columnconfigure(0, weight=1)

    def add_header(self, title: str, subtitle: str | None = None):
        """
        Add a standard page header.

        Parameters
        ----------
        title : str
            Main page title.

        subtitle : str | None
            Optional subtitle text.
        """

        header = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=self.PAGE_PAD_X,
            pady=(self.PAGE_PAD_Y, 10)
        )

        header.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        )

        title_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        if subtitle:
            subtitle_label = ctk.CTkLabel(
                header,
                text=subtitle,
                font=("Segoe UI", 13),
                anchor="w",
                text_color="gray"
            )

            subtitle_label.grid(
                row=1,
                column=0,
                sticky="w",
                pady=(4, 0)
            )

        return header

    def create_section(self, row: int, columns: int = 1):
        """
        Create a standard content section.

        Parameters
        ----------
        row : int
            Grid row inside the scrollable content.

        columns : int
            Number of responsive columns in the section.
        """

        section = ctk.CTkFrame(self.content)

        section.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=self.PAGE_PAD_X,
            pady=(0, self.SECTION_PAD_Y)
        )

        for column in range(columns):
            section.grid_columnconfigure(column, weight=1)

        return section