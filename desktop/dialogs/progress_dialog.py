"""Progress dialog used while Excel reports are generated."""
from __future__ import annotations

import customtkinter as ctk


class ReportProgressDialog(ctk.CTkToplevel):
    def __init__(self, master, report_title: str) -> None:
        super().__init__(master)
        self.title("Generating Report")
        self.geometry("500x245")
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        ctk.CTkLabel(self, text="⚙️", font=("Segoe UI Emoji", 38)).pack(pady=(24, 5))
        ctk.CTkLabel(
            self,
            text=f"Generating {report_title}",
            font=("Segoe UI", 19, "bold"),
        ).pack(pady=(0, 6))
        self.status_label = ctk.CTkLabel(
            self, text="Preparing export...", font=("Segoe UI", 12)
        )
        self.status_label.pack(pady=(0, 14))
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.pack(pady=4)
        self.progress.set(0)
        self.percent_label = ctk.CTkLabel(self, text="0%", font=("Segoe UI", 11))
        self.percent_label.pack(pady=7)

    def update_progress(self, value: int, message: str) -> None:
        bounded = max(0, min(100, int(value)))
        self.progress.set(bounded / 100)
        self.percent_label.configure(text=f"{bounded}%")
        self.status_label.configure(text=message)
        self.update_idletasks()
