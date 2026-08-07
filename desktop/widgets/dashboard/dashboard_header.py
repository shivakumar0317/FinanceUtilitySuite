"""
Finance Utility Suite
Dashboard Header Widget

Reusable header for the Enterprise Dashboard.

Author : Shiva Kumar
Version : 2.1.0
"""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class DashboardHeader(ctk.CTkFrame):
    """
    Enterprise Dashboard Header.

    Public Methods
    --------------
    set_status(text, color=None)
        Update engine status.

    set_refresh_callback(callback)
        Assign refresh button callback.
    """

    def __init__(self, master, **kwargs):

        super().__init__(
            master,
            fg_color="transparent",
            **kwargs,
        )

        self._refresh_callback: Callable | None = None
        self._report_callback: Callable | None = None

        self._build()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build(self):

        self.grid_columnconfigure(0, weight=1)

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------

        ctk.CTkLabel(
            self,
            text="Enterprise Risk Dashboard",
            font=("Segoe UI", 28, "bold"),
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        # -----------------------------------------------------
        # Status
        # -----------------------------------------------------

        self.status_label = ctk.CTkLabel(
            self,
            text="Risk Engine : Waiting",
            font=("Segoe UI", 11, "bold"),
            text_color="#3B82F6",
        )

        self.status_label.grid(
            row=0,
            column=1,
            padx=(12, 12),
            sticky="e",
        )

        # -----------------------------------------------------
        # Refresh
        # -----------------------------------------------------

        self.refresh_button = ctk.CTkButton(
            self,
            text="🔄 Refresh",
            width=110,
            command=self._on_refresh,
        )

        self.refresh_button.grid(
            row=0,
            column=2,
            padx=(0, 8),
        )

        self.report_button = ctk.CTkButton(
            self,
            text="📄 Report",
            width=120,
            fg_color="#1F4E78",
            hover_color="#163A5A",
            command=self._on_report,
        )

        self.report_button.grid(
            row=0,
            column=3,
        )

        # -----------------------------------------------------
        # Subtitle
        # -----------------------------------------------------

        ctk.CTkLabel(
            self,
            text=(
                "Centralized portfolio health, exposure, "
                "margin and concentration monitoring"
            ),
            font=("Segoe UI", 12),
            text_color=("#6B7280", "#9CA3AF"),
            anchor="w",
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(4, 0),
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def set_refresh_callback(
        self,
        callback: Callable,
    ):

        self._refresh_callback = callback

    def set_report_callback(
    self,
    callback: Callable,
    ):

        self._report_callback = callback    

    def set_status(
        self,
        text: str,
        color: str | None = None,
    ):

        self.status_label.configure(
            text=text,
        )

        if color:

            self.status_label.configure(
                text_color=color,
            )

    # ---------------------------------------------------------
    # Events
    # ---------------------------------------------------------

    def _on_refresh(self):

        if self._refresh_callback:

            self._refresh_callback()

    def _on_report(self):

        if self._report_callback:

            self._report_callback()        