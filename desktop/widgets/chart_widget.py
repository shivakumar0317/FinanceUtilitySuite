"""
Finance Utility Suite
Chart Widget

Reusable Matplotlib widget for CustomTkinter.
"""

from __future__ import annotations

from typing import Sequence

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.figure import Figure


class ChartWidget(ctk.CTkFrame):
    """
    Reusable chart widget.

    Current Features
    ----------------
    ✓ Line Chart
    ✓ Clear Chart
    ✓ Navigation Toolbar

    Upcoming
    --------
    ✓ Bar Chart
    ✓ Pie Chart
    ✓ Histogram
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._build_ui()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build_ui(self):

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.figure = Figure(
            figsize=(6, 4),
            dpi=100
        )

        self.axes = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        toolbar_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        toolbar_frame.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.toolbar = NavigationToolbar2Tk(
            self.canvas,
            toolbar_frame,
            pack_toolbar=False
        )

        self.toolbar.update()

        self.toolbar.pack(
            fill="x"
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def clear(self):
        """Clear the chart."""

        self.axes.clear()
        self.canvas.draw_idle()

    # ---------------------------------------------------------
    # Line Chart
    # ---------------------------------------------------------

    def plot_line(
        self,
        x: Sequence,
        y: Sequence,
        *,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        marker: str = "o",
    ):
        """
        Plot a line chart.
        """

        self.axes.clear()

        self.axes.plot(
            x,
            y,
            marker=marker,
            linewidth=2
        )

        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)

        self.axes.grid(
            True,
            linestyle="--",
            alpha=0.4
        )

        self.figure.tight_layout()

        self.canvas.draw_idle()