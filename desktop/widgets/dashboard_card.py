"""
Finance Utility Suite
Dashboard Card Widget

Reusable summary card used across dashboards, analytics,
portfolio, MTF and risk modules.

Author : Shiva Kumar
Version: 1.00
"""

from __future__ import annotations

import customtkinter as ctk

from desktop.theme import Theme


class DashboardCard(ctk.CTkFrame):
    """Reusable dashboard summary card."""

    CARD_HEIGHT = 140

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
        super().__init__(
            master,
            corner_radius=Theme.BORDER_RADIUS,
            height=self.CARD_HEIGHT,
            border_width=1,
            border_color=self.STATUS_COLORS["default"],
        )

        self.title_text = title
        self.value_text = str(value)
        self.subtitle_text = subtitle
        self.icon_text = icon
        self.status = status

        self.default_fg_color = self.cget("fg_color")
        self.hover_fg_color = getattr(Theme, "SURFACE_HOVER", "#2A2D2E")

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_ui()
        self._bind_hover()
        self.set_status(status)

    def _build_ui(self) -> None:
        """Build card UI."""

        self.title_label = ctk.CTkLabel(
            self,
            text=self._get_header_text(),
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=Theme.CARD_PADDING + 8,
            pady=(Theme.CARD_PADDING + 8, 2),
        )

        self.value_label = ctk.CTkLabel(
            self,
            text=self.value_text,
            font=ctk.CTkFont(
                family=Theme.FONT_FAMILY,
                size=30,
                weight="bold",
            ),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        self.value_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=Theme.CARD_PADDING + 8,
            pady=(4, 4),
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
            padx=Theme.CARD_PADDING + 8,
            pady=(0, Theme.CARD_PADDING + 8),
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
        """Update subtitle color and card border."""

        self.status = status

        color = self.STATUS_COLORS.get(
            status,
            self.STATUS_COLORS["default"],
        )

        self.subtitle_label.configure(text_color=color)
        self.configure(border_color=color)

    def clear(self) -> None:
        """Reset card value and subtitle."""

        self.set_value("-")
        self.set_subtitle("")
        self.set_status("default")

    def _refresh_title(self) -> None:
        """Refresh title label with optional icon."""

        self.title_label.configure(text=self._get_header_text())

    def _get_header_text(self) -> str:
        """Return title text with optional icon."""

        if self.icon_text:
            return f"{self.icon_text} {self.title_text}"

        return self.title_text

    def _bind_hover(self) -> None:
        """Bind hover effect to card and child widgets."""

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        for widget in self.winfo_children():
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event=None) -> None:
        """Apply hover background."""

        self.configure(fg_color=self.hover_fg_color)

    def _on_leave(self, _event=None) -> None:
        """Restore default background."""

        self.configure(fg_color=self.default_fg_color)