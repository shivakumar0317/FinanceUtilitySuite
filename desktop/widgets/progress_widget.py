"""
Finance Utility Suite
Progress Widget
"""

from __future__ import annotations

import customtkinter as ctk


class ProgressWidget(ctk.CTkFrame):
    """Reusable progress widget."""

    def __init__(
        self,
        master,
        title: str = "Progress",
    ):
        super().__init__(master)

        self._build_ui(title)

    def _build_ui(self, title: str) -> None:
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
        )

        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=(8, 5),
        )

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
        )

        self.status_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10,
        )

        self.progress = ctk.CTkProgressBar(self)

        self.progress.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=10,
            pady=8,
        )

        self.progress.set(0)

        self.percent_label = ctk.CTkLabel(
            self,
            text="0%",
        )

        self.percent_label.grid(
            row=3,
            column=0,
            sticky="e",
            padx=10,
            pady=(0, 10),
        )

    # ----------------------------------------
    # Public API
    # ----------------------------------------

    def reset(self) -> None:
        self.update_progress(
            0,
            "Ready",
        )

    def update_progress(
        self,
        value: float,
        status: str | None = None,
    ) -> None:
        """
        value between 0.0 and 1.0
        """

        value = max(0.0, min(1.0, value))

        self.progress.set(value)

        self.percent_label.configure(
            text=f"{value * 100:.0f}%"
        )

        if status is not None:
            self.status_label.configure(
                text=status
            )

    def complete(
        self,
        message: str = "Completed",
    ) -> None:
        self.update_progress(
            1.0,
            message,
        )