"""Reusable professional metric card."""
from __future__ import annotations
import customtkinter as ctk


class MetricCard(ctk.CTkFrame):
    def __init__(self, master, title: str, icon: str = "", value: str = "0", subtitle: str = ""):
        super().__init__(master, corner_radius=12, border_width=1)
        self.grid_columnconfigure(1, weight=1)

        self.icon_label = ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=24))
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(14, 10), pady=14)

        self.title_label = ctk.CTkLabel(self, text=title, anchor="w")
        self.title_label.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=(11, 0))

        self.value_label = ctk.CTkLabel(
            self, text=value, anchor="w", font=ctk.CTkFont(size=21, weight="bold")
        )
        self.value_label.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=(0, 2))

        self.subtitle_label = ctk.CTkLabel(self, text=subtitle, anchor="w", text_color=("#666666", "#AAAAAA"))
        self.subtitle_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 10))

    def set_value(self, value: str, subtitle: str | None = None) -> None:
        self.value_label.configure(text=value)
        if subtitle is not None:
            self.subtitle_label.configure(text=subtitle)
