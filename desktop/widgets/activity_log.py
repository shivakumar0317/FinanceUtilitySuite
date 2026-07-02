"""
Finance Utility Suite
Activity Log Widget
"""

from __future__ import annotations

from datetime import datetime

import customtkinter as ctk


class ActivityLog(ctk.CTkFrame):
    """Reusable activity log widget."""

    def __init__(
        self,
        master,
        title: str = "Activity Log",
        height: int = 180,
    ):
        super().__init__(master)

        self._build_ui(title, height)

    def _build_ui(
        self,
        title: str,
        height: int,
    ) -> None:

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
        )

        title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=(8, 5),
        )

        self.textbox = ctk.CTkTextbox(
            self,
            height=height,
            wrap="word",
        )

        self.textbox.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10),
        )

        self.textbox.configure(state="disabled")

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def clear(self) -> None:
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def log(self, message: str) -> None:
        self._write("•", message)

    def success(self, message: str) -> None:
        self._write("✔", message)

    def warning(self, message: str) -> None:
        self._write("⚠", message)

    def error(self, message: str) -> None:
        self._write("✖", message)

    # -------------------------------------------------
    # Internal
    # -------------------------------------------------

    def _write(
        self,
        icon: str,
        message: str,
    ) -> None:

        timestamp = datetime.now().strftime("%H:%M:%S")

        self.textbox.configure(state="normal")

        self.textbox.insert(
            "end",
            f"{timestamp}  {icon}  {message}\n",
        )

        self.textbox.see("end")

        self.textbox.configure(state="disabled")