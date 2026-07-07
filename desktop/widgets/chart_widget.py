"""
Finance Utility Suite
Chart Widget

Reusable Matplotlib chart engine used across Portfolio,
Analytics, Risk Dashboard and MTF modules.

Author : Shiva Kumar
Version: 1.00
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from desktop.theme import Theme


class ChartWidget(ctk.CTkFrame):
    """Reusable chart widget with toolbar and generic plotting API."""

    SUPPORTED_CHARTS = {"pie", "bar", "line"}

    DEFAULT_BAR_COLOR = "#2563EB"
    DEFAULT_LINE_COLOR = "#16A34A"
    DEFAULT_GRID_COLOR = "#3F3F46"
    DEFAULT_TEXT_COLOR = "#E5E7EB"
    DEFAULT_MUTED_TEXT_COLOR = "#A1A1AA"
    DEFAULT_FIGURE_BG = "#18181B"
    DEFAULT_AXIS_BG = "#18181B"

    PIE_COLORS = (
        "#2563EB",
        "#16A34A",
        "#D97706",
        "#DC2626",
        "#0891B2",
        "#7C3AED",
        "#DB2777",
        "#65A30D",
        "#EA580C",
        "#475569",
    )

    def __init__(
        self,
        master,
        title: str = "",
        figsize: tuple[int, int] = (6, 3),
        dpi: int = 100,
    ):
        super().__init__(
            master,
            corner_radius=Theme.BORDER_RADIUS,
        )

        self.title = title
        self.figsize = figsize
        self.dpi = dpi

        self.figure = Figure(figsize=self.figsize, dpi=self.dpi)
        self.axis = self.figure.add_subplot(111)

        self.canvas: FigureCanvasTkAgg | None = None
        self.toolbar: NavigationToolbar2Tk | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build chart container."""

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=Theme.CARD_PADDING,
            pady=(Theme.CARD_PADDING, 0),
        )

        self.toolbar = NavigationToolbar2Tk(
            self.canvas,
            self,
            pack_toolbar=False,
        )
        self.toolbar.update()
        self.toolbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=Theme.CARD_PADDING,
            pady=(0, Theme.CARD_PADDING),
        )

        self.clear("No chart data")

    def plot(self, chart_type: str, **kwargs: Any) -> None:
        """Generic chart plotting API."""

        chart_type = chart_type.lower().strip()

        if chart_type not in self.SUPPORTED_CHARTS:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        if chart_type == "pie":
            self._plot_pie_internal(
                labels=kwargs.get("labels", []),
                values=kwargs.get("values", []),
                title=kwargs.get("title", self.title),
            )

        elif chart_type == "bar":
            self._plot_bar_internal(
                x=kwargs.get("x", kwargs.get("labels", [])),
                y=kwargs.get("y", kwargs.get("values", [])),
                title=kwargs.get("title", self.title),
                xlabel=kwargs.get("xlabel", ""),
                ylabel=kwargs.get("ylabel", ""),
            )

        elif chart_type == "line":
            self._plot_line_internal(
                x=kwargs.get("x", kwargs.get("labels", [])),
                y=kwargs.get("y", kwargs.get("values", [])),
                title=kwargs.get("title", self.title),
                xlabel=kwargs.get("xlabel", ""),
                ylabel=kwargs.get("ylabel", ""),
            )

        self._redraw_chart()

    def set_title(self, title: str) -> None:
        """Update widget title used by plots."""

        self.title = title

    def plot_pie(
        self,
        labels: Sequence,
        values: Sequence,
        title: str = "",
    ) -> None:
        """Plot pie chart."""

        self.plot(
            chart_type="pie",
            labels=labels,
            values=values,
            title=title or self.title,
        )

    def plot_bar(
        self,
        x: Sequence | None = None,
        y: Sequence | None = None,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        labels: Sequence | None = None,
        values: Sequence | None = None,
    ) -> None:
        """Plot bar chart.

        Supports both:
        plot_bar(x=[...], y=[...])
        plot_bar(labels=[...], values=[...])
        """

        if x is None:
            x = labels or []

        if y is None:
            y = values or []

        self.plot(
            chart_type="bar",
            x=x,
            y=y,
            title=title or self.title,
            xlabel=xlabel,
            ylabel=ylabel,
        )

    def plot_line(
        self,
        x: Sequence | None = None,
        y: Sequence | None = None,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        labels: Sequence | None = None,
        values: Sequence | None = None,
    ) -> None:
        """Plot line chart."""

        if x is None:
            x = labels or []

        if y is None:
            y = values or []

        self.plot(
            chart_type="line",
            x=x,
            y=y,
            title=title or self.title,
            xlabel=xlabel,
            ylabel=ylabel,
        )

    def clear(self, message: str = "") -> None:
        """Clear chart and optionally show message."""

        self.axis = self._reset_axis()
        self.axis.set_axis_off()

        if message:
            self.axis.text(
                0.5,
                0.5,
                message,
                ha="center",
                va="center",
                fontsize=11,
                color=self._theme_value("TEXT_SECONDARY", self.DEFAULT_MUTED_TEXT_COLOR),
                transform=self.axis.transAxes,
            )

        self._redraw_chart()

    def _plot_pie_internal(
        self,
        labels: Sequence,
        values: Sequence,
        title: str = "",
    ) -> None:
        """Render pie chart."""

        self.axis = self._reset_axis()

        if len(labels) == 0 or len(values) == 0:
            self.clear("No pie chart data")
            return

        self.axis.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=self.PIE_COLORS[: len(values)],
            textprops={
                "color": self._theme_value("TEXT_PRIMARY", self.DEFAULT_TEXT_COLOR),
                "fontsize": 9,
            },
            wedgeprops={
                "linewidth": 1,
                "edgecolor": self._theme_value("CHART_BG", self.DEFAULT_AXIS_BG),
            },
        )

        self._apply_title(title)
        self.axis.axis("equal")

    def _plot_bar_internal(
        self,
        x: Sequence,
        y: Sequence,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
    ) -> None:
        """Render bar chart."""

        self.axis = self._reset_axis()

        if len(x) == 0 or len(y) == 0:
            self.clear("No bar chart data")
            return

        self.axis.bar(
            x,
            y,
            color=self._theme_value("PRIMARY", self.DEFAULT_BAR_COLOR),
            edgecolor=self._theme_value("PRIMARY", self.DEFAULT_BAR_COLOR),
            linewidth=0.5,
        )

        self._apply_title(title)
        self._apply_axis_labels(xlabel, ylabel)
        self._apply_financial_y_axis()
        self._apply_grid()
        self.axis.tick_params(axis="x", rotation=45)

    def _plot_line_internal(
        self,
        x: Sequence,
        y: Sequence,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
    ) -> None:
        """Render line chart."""

        self.axis = self._reset_axis()

        if len(x) == 0 or len(y) == 0:
            self.clear("No line chart data")
            return

        self.axis.plot(
            x,
            y,
            marker="o",
            linewidth=2,
            markersize=5,
            color=self._theme_value("SUCCESS", self.DEFAULT_LINE_COLOR),
        )

        self._apply_title(title)
        self._apply_axis_labels(xlabel, ylabel)
        self._apply_financial_y_axis()
        self._apply_grid()
        self.axis.tick_params(axis="x", rotation=45)

    def _reset_axis(self):
        """Reset figure and return a fresh styled axis."""

        self.figure.clear()

        figure_bg = self._theme_value("CHART_BG", self.DEFAULT_FIGURE_BG)
        axis_bg = self._theme_value("CHART_BG", self.DEFAULT_AXIS_BG)

        self.figure.patch.set_facecolor(figure_bg)

        axis = self.figure.add_subplot(111)
        axis.set_facecolor(axis_bg)
        axis.set_axis_on()

        self._style_axis(axis)

        return axis

    def _style_axis(self, axis) -> None:
        """Apply shared axis styling."""

        text_color = self._theme_value("TEXT_PRIMARY", self.DEFAULT_TEXT_COLOR)
        muted_color = self._theme_value(
            "TEXT_SECONDARY",
            self.DEFAULT_MUTED_TEXT_COLOR,
        )

        axis.tick_params(
            axis="both",
            colors=muted_color,
            labelsize=9,
        )

        for spine in axis.spines.values():
            spine.set_color(self._theme_value("BORDER_COLOR", "#3F3F46"))
            spine.set_linewidth(0.8)

        axis.xaxis.label.set_color(text_color)
        axis.yaxis.label.set_color(text_color)
        axis.title.set_color(text_color)

    def _apply_title(self, title: str) -> None:
        """Apply chart title."""

        self.axis.set_title(
            title,
            fontsize=12,
            fontweight="bold",
            color=self._theme_value("TEXT_PRIMARY", self.DEFAULT_TEXT_COLOR),
            pad=12,
        )

    def _apply_axis_labels(self, xlabel: str, ylabel: str) -> None:
        """Apply axis labels."""

        self.axis.set_xlabel(
            self._format_label(xlabel),
            fontsize=10,
            color=self._theme_value("TEXT_SECONDARY", self.DEFAULT_MUTED_TEXT_COLOR),
            labelpad=8,
        )
        self.axis.set_ylabel(
            self._format_label(ylabel),
            fontsize=10,
            color=self._theme_value("TEXT_SECONDARY", self.DEFAULT_MUTED_TEXT_COLOR),
            labelpad=8,
        )

    def _apply_grid(self) -> None:
        """Apply subtle chart grid."""

        self.axis.grid(
            True,
            axis="y",
            linestyle="--",
            linewidth=0.6,
            alpha=0.35,
            color=self._theme_value("GRID_COLOR", self.DEFAULT_GRID_COLOR),
        )
        self.axis.set_axisbelow(True)

    def _apply_financial_y_axis(self) -> None:
        """Apply Indian financial number formatting to Y axis."""

        self.axis.yaxis.set_major_formatter(
            FuncFormatter(lambda value, _position: self._format_number(value)),
        )

    def _format_number(self, value: float | int) -> str:
        """Format number using Indian financial units."""

        try:
            amount = float(value)
        except (TypeError, ValueError):
            return str(value)

        sign = "-" if amount < 0 else ""
        amount = abs(amount)

        if amount >= 10_000_000:
            return f"{sign}{amount / 10_000_000:.2f} Cr"

        if amount >= 100_000:
            return f"{sign}{amount / 100_000:.2f} L"

        if amount >= 1_000:
            return f"{sign}{amount / 1_000:.2f} K"

        if amount == int(amount):
            return f"{sign}{int(amount)}"

        return f"{sign}{amount:.2f}"

    def _format_label(self, label: str) -> str:
        """Improve common financial axis labels."""

        if not label:
            return ""

        cleaned = label.replace("_", " ").strip()

        replacements = {
            "BUY VALUE": "Buy Value (₹)",
            "Buy Value": "Buy Value (₹)",
            "Exposure": "Exposure (₹)",
            "Margin": "Margin (₹)",
            "MTM": "MTM (₹)",
            "MarkToMarket": "MTM (₹)",
        }

        return replacements.get(cleaned, cleaned)

    def _theme_value(self, name: str, fallback: str) -> str:
        """Safely read theme values with fallback."""

        return getattr(Theme, name, fallback)

    def _redraw_chart(self) -> None:
        """Redraw chart canvas."""

        if self.canvas is not None:
            self.figure.tight_layout(pad=2.0)
            self.canvas.draw_idle()