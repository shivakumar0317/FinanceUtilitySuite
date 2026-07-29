"""
Finance Utility Suite
Reusable Scrollable Frame

Author  : Shiva Kumar
Version : 1.0
"""

from __future__ import annotations

import customtkinter as ctk


class ScrollableFrame(ctk.CTkScrollableFrame):
    """Reusable vertically scrollable CustomTkinter content frame.

    CustomTkinter provides the canvas, scrollbar, mouse-wheel and touchpad
    integration. This wrapper standardizes the layout used by large Finance
    Utility Suite dashboards.
    """

    def __init__(
        self,
        master,
        *,
        width: int = 200,
        height: int = 200,
        corner_radius: int = 0,
        border_width: int = 0,
        fg_color: str | tuple[str, str] = "transparent",
        scrollbar_fg_color: str | tuple[str, str] | None = None,
        scrollbar_button_color: str | tuple[str, str] | None = None,
        scrollbar_button_hover_color: str | tuple[str, str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            fg_color=fg_color,
            scrollbar_fg_color=scrollbar_fg_color,
            scrollbar_button_color=scrollbar_button_color,
            scrollbar_button_hover_color=scrollbar_button_hover_color,
            orientation="vertical",
            **kwargs,
        )

        self.grid_columnconfigure(0, weight=1)

    def scroll_to_top(self) -> None:
        """Move the dashboard viewport to the beginning."""

        canvas = getattr(self, "_parent_canvas", None)
        if canvas is not None:
            canvas.yview_moveto(0.0)

    def scroll_to_bottom(self) -> None:
        """Move the dashboard viewport to the end."""

        canvas = getattr(self, "_parent_canvas", None)
        if canvas is not None:
            canvas.yview_moveto(1.0)
