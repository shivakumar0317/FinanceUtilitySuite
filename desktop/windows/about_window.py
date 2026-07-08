"""
Finance Utility Suite
About Window

Professional application information dialog.

Author : Shiva Kumar
Version: 1.00
"""

from __future__ import annotations

import platform
import sys

import customtkinter as ctk

from desktop.theme import Theme


class AboutWindow(ctk.CTkToplevel):
    """About dialog for Finance Utility Suite."""

    def __init__(self, master):
        super().__init__(master)

        self.title("About Finance Utility Suite")
        self.geometry("460x420")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self._center_window()

    def _build_ui(self) -> None:
        title = ctk.CTkLabel(
            self,
            text=Theme.APP_NAME,
            font=ctk.CTkFont(
                family=Theme.FONT_FAMILY,
                size=26,
                weight="bold",
            ),
        )
        title.grid(row=0, column=0, pady=(30, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Portfolio • Risk • Analytics",
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.TEXT_SECONDARY,
        )
        subtitle.grid(row=1, column=0, pady=(0, 20))

        version = ctk.CTkLabel(
            self,
            text=f"Version {Theme.VERSION}",
            font=Theme.FONT_HEADING,
        )
        version.grid(row=2, column=0, pady=(0, 20))

        info = ctk.CTkFrame(
            self,
            corner_radius=Theme.BORDER_RADIUS,
        )
        info.grid(row=3, column=0, sticky="ew", padx=35, pady=(0, 20))
        info.grid_columnconfigure(1, weight=1)

        rows = [
            ("Developer", "Siva Kumar.R"),
            ("Python", sys.version.split()[0]),
            ("Platform", platform.system()),
            ("UI Framework", "CustomTkinter"),
            ("Data Engine", "Pandas / OpenPyXL"),
            ("Charts", "Matplotlib"),
        ]

        for index, (label, value) in enumerate(rows):
            key = ctk.CTkLabel(
                info,
                text=f"{label}:",
                font=Theme.FONT_SMALL,
                text_color=Theme.TEXT_SECONDARY,
                anchor="w",
            )
            key.grid(
                row=index,
                column=0,
                sticky="w",
                padx=(15, 8),
                pady=7,
            )

            val = ctk.CTkLabel(
                info,
                text=value,
                font=Theme.FONT_SMALL,
                anchor="w",
            )
            val.grid(
                row=index,
                column=1,
                sticky="w",
                padx=(0, 15),
                pady=7,
            )

        copyright_label = ctk.CTkLabel(
            self,
            text="© 2026 Siva Kumar.R. All rights reserved.",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        )
        copyright_label.grid(row=4, column=0, pady=(5, 20))

        close_button = ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            width=120,
            height=Theme.BUTTON_HEIGHT,
        )
        close_button.grid(row=5, column=0, pady=(0, 25))

    def _center_window(self) -> None:
        self.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()

        x = self.winfo_screenwidth() // 2 - width // 2
        y = self.winfo_screenheight() // 2 - height // 2

        self.geometry(f"{width}x{height}+{x}+{y}")