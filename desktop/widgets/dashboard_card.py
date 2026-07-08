"""
Finance Utility Suite
Dashboard Card Widget

Author : Shiva Kumar
Version: 1.01
"""

from __future__ import annotations

import customtkinter as ctk

from desktop.theme import Theme


class DashboardCard(ctk.CTkFrame):
    """Reusable dashboard summary card."""

    CARD_HEIGHT = 120

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
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title_text,
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=Theme.CARD_PADDING,
            pady=(Theme.CARD_PADDING, 0),
        )

        self.icon_label = ctk.CTkLabel(
            self,
            text=self.icon_text,
            font=ctk.CTkFont(
                family=Theme.FONT_FAMILY,
                size=22,
                weight="bold",
            ),
            text_color=Theme.PRIMARY,
        )
        self.icon_label.place(
            relx=0.90,
            rely=0.25,
            anchor="center",
        )

        self.value_label = ctk.CTkLabel(
            self,
            text=self.value_text,
            font=ctk.CTkFont(
                family=Theme.FONT_FAMILY,
                size=24,
                weight="bold",
            ),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        self.value_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=Theme.CARD_PADDING,
            pady=(2, 2),
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
            padx=Theme.CARD_PADDING,
            pady=(0, Theme.CARD_PADDING),
        )

    def set_value(self, value: str | int | float) -> None:
        self.value_text = str(value)
        self.value_label.configure(text=self.value_text)

    def set_value_color(self, color: str) -> None:
        self.value_label.configure(text_color=color)

    def set_subtitle(self, subtitle: str) -> None:
        self.subtitle_text = subtitle
        self.subtitle_label.configure(text=self.subtitle_text)

    def set_title(self, title: str) -> None:
        self.title_text = title
        self.title_label.configure(text=self.title_text)

    def set_icon(self, icon: str) -> None:
        self.icon_text = icon
        self.icon_label.configure(text=self.icon_text)

    def set_status(self, status: str = "default") -> None:
        self.status = status

        color = self.STATUS_COLORS.get(
            status,
            self.STATUS_COLORS["default"],
        )

        self.subtitle_label.configure(text_color=color)
        self.configure(border_color=color)

    def clear(self) -> None:
        self.set_value("-")
        self.set_subtitle("")
        self.set_icon("")
        self.set_value_color(Theme.TEXT_PRIMARY)
        self.set_status("default")

    def _bind_hover(self) -> None:
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        for widget in self.winfo_children():
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event=None) -> None:
        self.configure(fg_color=self.hover_fg_color)

    def _on_leave(self, _event=None) -> None:
        self.configure(fg_color=self.default_fg_color)