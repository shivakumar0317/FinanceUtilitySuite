"""Finance Utility Suite Report Center page - Sprint 2."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tkinter import messagebox
import threading
import time

import customtkinter as ctk

from desktop.dialogs.export_report_dialog import ExportReportDialog, ExportRequest
from desktop.dialogs.progress_dialog import ReportProgressDialog
from desktop.dialogs.report_success_dialog import ReportSuccessDialog, open_path
from desktop.reports.report_export_service import ReportExportService
from desktop.reports.report_registry import ReportDefinition, ReportRegistry, get_report_registry
from desktop.widgets.report_card import ReportCard


class ReportsPage(ctk.CTkFrame):
    """Registry-driven Report Center with end-to-end Excel export workflow."""

    def __init__(
        self,
        master,
        *,
        registry: ReportRegistry | None = None,
        on_generate: Callable[[ReportDefinition], None] | None = None,
    ) -> None:
        super().__init__(master)
        self.registry = registry or get_report_registry()
        self.on_generate = on_generate
        self.search_var = ctk.StringVar(value="")
        self._build_ui()
        self._render_cards()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Report Center", font=("Segoe UI", 28, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(
            header,
            text="Generate professional portfolio, analytics and client reports.",
            font=("Segoe UI", 12),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        search = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text="Search reports...",
            height=38,
        )
        search.grid(row=1, column=0, sticky="ew", padx=24, pady=(4, 12))
        self.search_var.trace_add("write", lambda *_: self._render_cards())

        self.cards_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.cards_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))

    def _render_cards(self) -> None:
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        reports = self.registry.search(self.search_var.get())
        columns = 2
        for column in range(columns):
            self.cards_frame.grid_columnconfigure(column, weight=1, uniform="report-card")

        if not reports:
            ctk.CTkLabel(
                self.cards_frame,
                text="No reports match your search.",
                font=("Segoe UI", 14),
            ).grid(row=0, column=0, columnspan=columns, padx=20, pady=50)
            return

        for index, report in enumerate(reports):
            row, column = divmod(index, columns)
            ReportCard(
                self.cards_frame,
                report=report,
                on_generate=self._generate_report,
            ).grid(row=row, column=column, sticky="nsew", padx=10, pady=10)

    def _generate_report(self, report: ReportDefinition) -> None:
        if self.on_generate is not None:
            self.on_generate(report)
            return

        export_request = ExportReportDialog(self, report).show()
        if export_request is None:
            return
        self._start_export(report, export_request)

    def _start_export(self, report: ReportDefinition, request: ExportRequest) -> None:
        progress_dialog = ReportProgressDialog(self, report.title)
        started = time.perf_counter()

        def progress(value: int, message: str) -> None:
            self.after(0, lambda: progress_dialog.update_progress(value, message))

        def worker() -> None:
            try:
                output = ReportExportService.export(request.export, progress=progress)
            except Exception as exc:
                self.after(0, lambda error=exc: self._export_failed(progress_dialog, error))
                return
            elapsed = time.perf_counter() - started
            self.after(
                0,
                lambda: self._export_succeeded(progress_dialog, request, output, elapsed),
            )

        threading.Thread(target=worker, daemon=True, name="report-export").start()

    def _export_failed(self, progress_dialog: ReportProgressDialog, error: Exception) -> None:
        if progress_dialog.winfo_exists():
            progress_dialog.grab_release()
            progress_dialog.destroy()
        messagebox.showerror("Report Generation Failed", str(error), parent=self)

    def _export_succeeded(
        self,
        progress_dialog: ReportProgressDialog,
        request: ExportRequest,
        output: Path,
        elapsed: float,
    ) -> None:
        if progress_dialog.winfo_exists():
            progress_dialog.update_progress(100, "Report generated successfully.")
            progress_dialog.grab_release()
            progress_dialog.destroy()

        if request.open_report:
            try:
                open_path(output)
            except Exception:
                pass
        if request.open_folder:
            try:
                open_path(output.parent)
            except Exception:
                pass

        ReportSuccessDialog(self, output, elapsed)
