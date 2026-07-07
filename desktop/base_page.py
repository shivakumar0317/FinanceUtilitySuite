"""
Finance Utility Suite
Base Page

Reusable base class for all application pages.

Author : Shiva Kumar
Version : 0.99
"""

from __future__ import annotations

import customtkinter as ctk


class BasePage(ctk.CTkFrame):
    """Base class for all application pages."""

    def __init__(self, master, title: str):
        super().__init__(master)

        self.page_title = title

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_content_area()

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    def _create_header(self) -> None:
        self.header = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(15, 10),
        )

        self.header.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header,
            text=self.page_title,
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )

        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.status_label = ctk.CTkLabel(
            self.header,
            text="Ready",
        )

        self.status_label.grid(
            row=0,
            column=1,
            sticky="e",
        )

    # --------------------------------------------------
    # Scrollable Content Area
    # --------------------------------------------------

    def _create_content_area(self) -> None:
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )

        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        self.content.grid_columnconfigure(0, weight=1)

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def set_status(self, message: str) -> None:
        self.status_label.configure(text=message)

    def set_title(self, title: str) -> None:
        self.page_title = title
        self.title_label.configure(text=title)