"""Reusable Report Center export-input dialog."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from desktop.reports.report_export_service import ReportExportRequest, ReportExportService
from desktop.reports.report_registry import ReportDefinition


@dataclass(frozen=True, slots=True)
class ExportRequest:
    """UI result returned to the Report Center page."""

    export: ReportExportRequest
    open_report: bool
    open_folder: bool


class ExportReportDialog(ctk.CTkToplevel):
    """Collect report source, destination and report-specific options."""

    def __init__(self, master, report: ReportDefinition) -> None:
        super().__init__(master)
        self.report = report
        self.result: ExportRequest | None = None

        self.title(f"Generate {report.title}")
        self.geometry("650x560" if report.report_id == "analytics" else "650x500")
        self.minsize(620, 470)
        self.transient(master.winfo_toplevel())
        self.grab_set()

        self.source_var = ctk.StringVar(value="")
        self.history_var = ctk.StringVar(value="")
        self.output_var = ctk.StringVar(value="")
        self.subject_var = ctk.StringVar(
            value="CLIENT" if report.report_id == "client_holdings" else "My Portfolio"
        )
        self.open_report_var = ctk.BooleanVar(value=True)
        self.open_folder_var = ctk.BooleanVar(value=False)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=26, pady=(22, 12))
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text=self.report.icon, font=("Segoe UI Emoji", 36)).grid(
            row=0, column=0, rowspan=2, padx=(0, 14)
        )
        ctk.CTkLabel(
            header, text=self.report.title, font=("Segoe UI", 22, "bold"), anchor="w"
        ).grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(
            header,
            text="Select the data file and where the generated Excel report should be saved.",
            font=("Segoe UI", 11),
            anchor="w",
        ).grid(row=1, column=1, sticky="ew", pady=(3, 0))

        form = ctk.CTkFrame(self, corner_radius=12)
        form.grid(row=1, column=0, sticky="nsew", padx=26, pady=8)
        form.grid_columnconfigure(0, weight=1)

        subject_label = "Account ID" if self.report.report_id == "client_holdings" else "Portfolio Name"
        self._field(form, 0, subject_label, self.subject_var)
        self._file_field(form, 1, "Portfolio / Holdings Data", self.source_var, self._browse_source)

        next_row = 2
        if self.report.report_id == "analytics":
            self._file_field(
                form,
                next_row,
                "Historical Values (Optional)",
                self.history_var,
                self._browse_history,
            )
            next_row += 1

        self._file_field(form, next_row, "Save Report As", self.output_var, self._browse_output)

        options = ctk.CTkFrame(form, fg_color="transparent")
        options.grid(row=next_row + 1, column=0, sticky="ew", padx=18, pady=(8, 16))
        ctk.CTkCheckBox(
            options, text="Open report after export", variable=self.open_report_var
        ).pack(anchor="w", pady=4)
        ctk.CTkCheckBox(
            options, text="Open containing folder after export", variable=self.open_folder_var
        ).pack(anchor="w", pady=4)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=26, pady=(12, 22))
        actions.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(actions, text="Cancel", width=120, command=self._cancel).grid(
            row=0, column=1, padx=(8, 0)
        )
        ctk.CTkButton(
            actions, text="Generate Report", width=170, command=self._submit
        ).grid(row=0, column=2, padx=(8, 0))

    @staticmethod
    def _field(master, row: int, label: str, variable: ctk.Variable) -> None:
        wrapper = ctk.CTkFrame(master, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", padx=18, pady=(14, 2))
        wrapper.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(wrapper, text=label, font=("Segoe UI", 11, "bold"), anchor="w").grid(
            row=0, column=0, sticky="ew", pady=(0, 5)
        )
        ctk.CTkEntry(wrapper, textvariable=variable, height=36).grid(
            row=1, column=0, sticky="ew"
        )

    @staticmethod
    def _file_field(master, row: int, label: str, variable: ctk.Variable, command) -> None:
        wrapper = ctk.CTkFrame(master, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", padx=18, pady=(14, 2))
        wrapper.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(wrapper, text=label, font=("Segoe UI", 11, "bold"), anchor="w").grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5)
        )
        ctk.CTkEntry(wrapper, textvariable=variable, height=36).grid(
            row=1, column=0, sticky="ew", padx=(0, 8)
        )
        ctk.CTkButton(wrapper, text="Browse...", width=110, command=command).grid(
            row=1, column=1
        )

    def _browse_source(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="Select portfolio or holdings data",
            filetypes=[("Excel or CSV", "*.xlsx *.xls *.csv"), ("All files", "*.*")],
        )
        if path:
            self.source_var.set(path)
            if not self.output_var.get().strip():
                self._set_default_output(Path(path).parent)

    def _browse_history(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="Select historical portfolio values",
            filetypes=[("Excel or CSV", "*.xlsx *.xls *.csv"), ("All files", "*.*")],
        )
        if path:
            self.history_var.set(path)

    def _browse_output(self) -> None:
        subject = self.subject_var.get().strip() or "Report"
        filename = ReportExportService.default_filename(self.report, subject)
        path = filedialog.asksaveasfilename(
            parent=self,
            title=f"Save {self.report.title}",
            initialfile=filename,
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
        )
        if path:
            self.output_var.set(path)

    def _set_default_output(self, folder: Path) -> None:
        filename = ReportExportService.default_filename(
            self.report, self.subject_var.get().strip() or "Report"
        )
        self.output_var.set(str(folder / filename))

    def _submit(self) -> None:
        source = self.source_var.get().strip()
        output = self.output_var.get().strip()
        if not source:
            messagebox.showwarning("Generate Report", "Select a source data file.", parent=self)
            return
        if not output:
            messagebox.showwarning("Generate Report", "Choose the output report file.", parent=self)
            return

        try:
            request = ReportExportRequest(
                report_id=self.report.report_id,
                source_path=Path(source),
                output_path=Path(output),
                portfolio_name=self.subject_var.get(),
                account_id=self.subject_var.get(),
                history_path=Path(self.history_var.get()) if self.history_var.get().strip() else None,
            )
        except Exception as exc:
            messagebox.showerror("Generate Report", str(exc), parent=self)
            return

        self.result = ExportRequest(
            export=request,
            open_report=bool(self.open_report_var.get()),
            open_folder=bool(self.open_folder_var.get()),
        )
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    def show(self) -> ExportRequest | None:
        self.wait_window()
        return self.result
