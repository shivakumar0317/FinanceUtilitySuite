"""
Finance Utility Suite
Dashboard Card Widget

Reusable summary card used across dashboards, analytics,
portfolio, MTF and risk modules.

Author : Shiva Kumar
Version: 0.95
"""

from __future__ import annotations

import customtkinter as ctk

from desktop.theme import Theme


class DashboardCard(ctk.CTkFrame):
    """Reusable dashboard summary card."""

    STATUS_COLORS = {
        "default": Theme.TEXT_SECONDARY,
        "success": Theme.SUCCESS,
        "warning": Theme.WARNING,
        "error": Theme.ERROR,
        "info": Theme.INFO,
    }

    def __init__(
        self,
        master,
        title: str,
        value: str | int | float = "-",
        subtitle: str = "",
        icon: str = "",
        status: str = "default",
    ):
        super().__init__(master, corner_radius=Theme.BORDER_RADIUS)

        self.title_text = title
        self.value_text = str(value)
        self.subtitle_text = subtitle
        self.icon_text = icon
        self.status = status

        self.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self.set_status(status)

    def _build_ui(self) -> None:
        """Build card UI."""

        header_text = self.title_text

        if self.icon_text:
            header_text = f"{self.icon_text} {self.title_text}"

        self.title_label = ctk.CTkLabel(
            self,
            text=header_text,
            font=Theme.FONT_SUBHEADING,
            anchor="w",
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=Theme.CARD_PADDING + 6,
            pady=(Theme.CARD_PADDING + 6, 4),
        )

        self.value_label = ctk.CTkLabel(
            self,
            text=self.value_text,
            font=Theme.FONT_HEADING,
            anchor="w",
        )
        self.value_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=Theme.CARD_PADDING + 6,
            pady=(6, 4),
        )

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=self.subtitle_text,
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        self.subtitle_label.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=Theme.CARD_PADDING + 6,
            pady=(0, Theme.CARD_PADDING + 6),
        )

    def set_value(self, value: str | int | float) -> None:
        """Update card value."""

        self.value_text = str(value)
        self.value_label.configure(text=self.value_text)

    def set_subtitle(self, subtitle: str) -> None:
        """Update card subtitle."""

        self.subtitle_text = subtitle
        self.subtitle_label.configure(text=self.subtitle_text)

    def set_title(self, title: str) -> None:
        """Update card title."""

        self.title_text = title
        self._refresh_title()

    def set_icon(self, icon: str) -> None:
        """Update card icon."""

        self.icon_text = icon
        self._refresh_title()

    def set_status(self, status: str = "default") -> None:
        """Update subtitle/status color."""

        self.status = status

        color = self.STATUS_COLORS.get(
            status,
            self.STATUS_COLORS["default"],
        )

        self.subtitle_label.configure(text_color=color)

    def clear(self) -> None:
        """Reset card value and subtitle."""

        self.set_value("-")
        self.set_subtitle("")
        self.set_status("default")

    def _refresh_title(self) -> None:
        """Refresh title label with optional icon."""

        title = self.title_text

        if self.icon_text:
            title = f"{self.icon_text} {self.title_text}"

        self.title_label.configure(text=title)
