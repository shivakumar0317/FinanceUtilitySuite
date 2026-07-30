"""Reusable Report Center card widget."""
from __future__ import annotations

from collections.abc import Callable
import customtkinter as ctk

from desktop.reports.report_registry import ReportDefinition


class ReportCard(ctk.CTkFrame):
    """Visual card for one :class:`ReportDefinition`."""

    def __init__(
        self,
        master,
        report: ReportDefinition,
        on_generate: Callable[[ReportDefinition], None] | None = None,
    ) -> None:
        super().__init__(master, corner_radius=12, border_width=1)
        self.report = report
        self.on_generate = on_generate
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        icon = ctk.CTkLabel(self, text=self.report.icon, font=("Segoe UI Emoji", 30))
        icon.grid(row=0, column=0, rowspan=2, padx=(18, 12), pady=(18, 8), sticky="n")

        title = ctk.CTkLabel(
            self,
            text=self.report.title,
            font=("Segoe UI", 17, "bold"),
            anchor="w",
        )
        title.grid(row=0, column=1, padx=(0, 18), pady=(18, 4), sticky="ew")

        description = ctk.CTkLabel(
            self,
            text=self.report.description,
            font=("Segoe UI", 11),
            justify="left",
            anchor="nw",
            wraplength=290,
        )
        description.grid(row=1, column=1, padx=(0, 18), pady=(0, 12), sticky="nsew")

        button_text = "Generate Report" if self.report.is_available else "Coming Soon"
        button = ctk.CTkButton(
            self,
            text=button_text,
            height=36,
            state="normal" if self.report.is_available else "disabled",
            command=self._handle_generate,
        )
        button.grid(row=2, column=0, columnspan=2, padx=18, pady=(4, 18), sticky="ew")

    def _handle_generate(self) -> None:
        if self.report.is_available and self.on_generate is not None:
            self.on_generate(self.report)
