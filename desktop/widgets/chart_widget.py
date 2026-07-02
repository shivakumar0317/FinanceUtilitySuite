"""
Finance Utility Suite
Chart Widget

Reusable Matplotlib chart engine used across Portfolio,
Analytics, Risk Dashboard and MTF modules.

Author : Shiva Kumar
Version: 0.95
"""

from __future__ import annotations

from collections.abc import Sequence

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from desktop.theme import Theme


class ChartWidget(ctk.CTkFrame):
    """Reusable chart widget with toolbar and generic plotting API."""

    SUPPORTED_CHARTS = {"pie", "bar", "line"}

    def __init__(
        self,
        master,
        title: str = "",
        figsize: tuple[int, int] = (5, 3),
        dpi: int = 100,
    ):
        super().__init__(master, corner_radius=Theme.BORDER_RADIUS)

        self.title = title
        self.figsize = figsize
        self.dpi = dpi

        self.figure = Figure(figsize=self.figsize, dpi=self.dpi)
        self.axis = self.figure.add_subplot(111)

        self.canvas = None
        self.toolbar = None

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

    def plot(self, chart_type: str, **kwargs) -> None:
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
                x=kwargs.get("x", []),
                y=kwargs.get("y", []),
                title=kwargs.get("title", self.title),
                xlabel=kwargs.get("xlabel", ""),
                ylabel=kwargs.get("ylabel", ""),
            )

        elif chart_type == "line":
            self._plot_line_internal(
                x=kwargs.get("x", []),
                y=kwargs.get("y", []),
                title=kwargs.get("title", self.title),
                xlabel=kwargs.get("xlabel", ""),
                ylabel=kwargs.get("ylabel", ""),
            )

        self._redraw_chart()

    def plot_pie(self, labels: Sequence, values: Sequence, title: str = "") -> None:
        """Backward-compatible pie chart method."""

        self.plot(
            chart_type="pie",
            labels=labels,
            values=values,
            title=title,
        )

    def plot_bar(
        self,
        x: Sequence,
        y: Sequence,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
    ) -> None:
        """Backward-compatible bar chart method."""

        self.plot(
            chart_type="bar",
            x=x,
            y=y,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
        )

    def plot_line(
        self,
        x: Sequence,
        y: Sequence,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
    ) -> None:
        """Plot line chart."""

        self.plot(
            chart_type="line",
            x=x,
            y=y,
            title=title,
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
                color="gray",
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
        )

        self.axis.set_title(title, fontsize=12, fontweight="bold")

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

        self.axis.bar(x, y)
        self.axis.set_title(title, fontsize=12, fontweight="bold")
        self.axis.set_xlabel(xlabel)
        self.axis.set_ylabel(ylabel)
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

        self.axis.plot(x, y, marker="o")
        self.axis.set_title(title, fontsize=12, fontweight="bold")
        self.axis.set_xlabel(xlabel)
        self.axis.set_ylabel(ylabel)
        self.axis.tick_params(axis="x", rotation=45)

    def _reset_axis(self):
        """Reset figure and return a fresh axis."""

        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.set_axis_on()

        return axis

    def _redraw_chart(self) -> None:
        """Redraw chart canvas."""

        if self.canvas is not None:
            self.figure.tight_layout()
            self.canvas.draw()
