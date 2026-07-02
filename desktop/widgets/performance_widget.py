"""
Finance Utility Suite
Performance Widget

Reusable metrics panel for portfolio, MTF, risk dashboard
and analytics performance summaries.

Author : Shiva Kumar
Version: 0.95
"""

from __future__ import annotations

import customtkinter as ctk

from desktop.theme import Theme


class PerformanceWidget(ctk.CTkFrame):
    """Reusable performance summary widget."""

    DEFAULT_METRICS = [
        "Best Performer",
        "Worst Performer",
        "Average Return",
        "Winning Stocks",
        "Losing Stocks",
        "Total Profit",
    ]

    STATUS_MAP = {
        "Best Performer": "success",
        "Worst Performer": "error",
        "Average Return": "info",
        "Winning Stocks": "success",
        "Losing Stocks": "error",
        "Total Profit": "success",
    }

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
        title: str = "Portfolio Performance",
        metrics: list[str] | None = None,
    ):
        super().__init__(master, corner_radius=Theme.BORDER_RADIUS)

        self.title = title
        self.metrics = metrics or self.DEFAULT_METRICS
        self.metric_labels: dict[str, ctk.CTkLabel] = {}

        self._build_ui()

    def _build_ui(self) -> None:
        """Build performance widget UI."""

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=Theme.FONT_SUBHEADING,
            anchor="w",
        )
        title_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=Theme.CARD_PADDING + 8,
            pady=(Theme.CARD_PADDING + 8, 12),
        )

        for index, metric in enumerate(self.metrics, start=1):
            self._create_metric_row(index, metric)

    def _create_metric_row(self, row: int, metric: str) -> None:
        """Create one metric/value row."""

        name_label = ctk.CTkLabel(
            self,
            text=metric,
            anchor="w",
            font=Theme.FONT_NORMAL,
            text_color=Theme.TEXT_SECONDARY,
        )
        name_label.grid(
            row=row,
            column=0,
            sticky="w",
            padx=Theme.CARD_PADDING + 12,
            pady=6,
        )

        value_label = ctk.CTkLabel(
            self,
            text="-",
            anchor="e",
            font=Theme.FONT_NORMAL,
        )
        value_label.grid(
            row=row,
            column=1,
            sticky="e",
            padx=Theme.CARD_PADDING + 12,
            pady=6,
        )

        self.metric_labels[metric] = value_label

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def update_metrics(self, metrics: dict) -> None:
        """Update displayed metrics."""

        for key, value in metrics.items():
            if key not in self.metric_labels:
                continue

            label = self.metric_labels[key]
            label.configure(text=str(value))

            status = self.STATUS_MAP.get(key, "default")
            color = self.STATUS_COLORS.get(status, Theme.TEXT_SECONDARY)
            label.configure(text_color=color)

    def set_metric(self, metric: str, value: str, status: str = "default") -> None:
        """Update a single metric value."""

        if metric not in self.metric_labels:
            return

        color = self.STATUS_COLORS.get(status, Theme.TEXT_SECONDARY)

        self.metric_labels[metric].configure(
            text=str(value),
            text_color=color,
        )

    def clear(self) -> None:
        """Reset all metrics."""

        for label in self.metric_labels.values():
            label.configure(
                text="-",
                text_color=Theme.TEXT_SECONDARY,
            )
