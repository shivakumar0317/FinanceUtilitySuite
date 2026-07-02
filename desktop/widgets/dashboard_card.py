"""
Finance Utility Suite
Dashboard Card Widget
"""

from __future__ import annotations

import customtkinter as ctk


class DashboardCard(ctk.CTkFrame):
    """
    Reusable dashboard statistic card.

    Parameters
    ----------
    title : str
        Card title.

    value : str
        Main value.

    subtitle : str
        Small information below value.
    """

    def __init__(
        self,
        master,
        title="Title",
        value="0",
        subtitle="",
        width=250,
        height=140,
        **kwargs,
    ):
        super().__init__(master, width=width, height=height, corner_radius=12, **kwargs)

        self.grid_propagate(False)

        self.title = title
        self.value = value
        self.subtitle = subtitle

        self._build_ui()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def _build_ui(self):

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title

        self.title_label = ctk.CTkLabel(
            self, text=self.title, font=("Segoe UI", 15, "bold"), anchor="w"
        )

        self.title_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))

        # Value

        self.value_label = ctk.CTkLabel(
            self, text=self.value, font=("Segoe UI", 28, "bold"), anchor="w"
        )

        self.value_label.grid(row=1, column=0, sticky="sw", padx=20)

        # Subtitle

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=self.subtitle,
            font=("Segoe UI", 12),
            text_color="gray70",
            anchor="w",
        )

        self.subtitle_label.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 15))

    # --------------------------------------------------
    # Update Methods
    # --------------------------------------------------

    def set_title(self, text: str):

        self.title = text
        self.title_label.configure(text=text)

    def set_value(self, value):

        self.value = value
        self.value_label.configure(text=str(value))

    def set_subtitle(self, text):

        self.subtitle = text
        self.subtitle_label.configure(text=text)
