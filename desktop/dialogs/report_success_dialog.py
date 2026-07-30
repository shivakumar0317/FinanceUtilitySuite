"""Completion dialog for Report Center exports."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import customtkinter as ctk


def open_path(path: str | Path) -> None:
    target = str(Path(path))
    if sys.platform.startswith("win"):
        os.startfile(target)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target])


class ReportSuccessDialog(ctk.CTkToplevel):
    def __init__(self, master, output_path: str | Path, elapsed_seconds: float) -> None:
        super().__init__(master)
        self.output_path = Path(output_path)
        self.title("Report Generated")
        self.geometry("570x340")
        self.resizable(False, False)
        self.transient(master.winfo_toplevel())
        self.grab_set()

        ctk.CTkLabel(self, text="✅", font=("Segoe UI Emoji", 42)).pack(pady=(24, 7))
        ctk.CTkLabel(
            self, text="Report Generated Successfully", font=("Segoe UI", 20, "bold")
        ).pack()
        ctk.CTkLabel(
            self,
            text=self.output_path.name,
            font=("Segoe UI", 13, "bold"),
        ).pack(pady=(12, 2))
        ctk.CTkLabel(
            self,
            text=str(self.output_path),
            font=("Segoe UI", 10),
            wraplength=500,
        ).pack(padx=24)
        ctk.CTkLabel(
            self, text=f"Generation time: {elapsed_seconds:.2f} seconds", font=("Segoe UI", 11)
        ).pack(pady=(10, 16))

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=6)
        ctk.CTkButton(
            actions, text="Open Report", width=135, command=lambda: open_path(self.output_path)
        ).grid(row=0, column=0, padx=5)
        ctk.CTkButton(
            actions,
            text="Open Folder",
            width=135,
            command=lambda: open_path(self.output_path.parent),
        ).grid(row=0, column=1, padx=5)
        ctk.CTkButton(actions, text="Close", width=110, command=self.destroy).grid(
            row=0, column=2, padx=5
        )
