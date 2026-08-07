"""
Finance Utility Suite
Enterprise RMS

Widget:
    Historical Chart Widget

Description:
    Reusable chart widget for historical analytics,
    dashboard trends and reports.

Version:
    3.0
"""

from __future__ import annotations

import customtkinter as ctk
import pandas as pd

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter


class HistoricalChartWidget(ctk.CTkFrame):
    """
    Historical chart widget.
    """

    def __init__(
        self,
        parent,
        title: str = "Chart",
        width: int = 700,
        height: int = 300,
    ):

        super().__init__(parent, corner_radius=12)

        self.title = title

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_lbl = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(
                size=18,
                weight="bold",
            ),
        )

        title_lbl.grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(12, 5),
        )

        self.figure = Figure(
            figsize=(8, 4.5),
            dpi=100,
        )

        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=self,
        )

        self.canvas.get_tk_widget().grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10),
        )

    # ---------------------------------------------------------

    def plot(
        self,
        labels: list,
        values: list,
    ):

        self.ax.clear()

        if not labels or not values:

            self.ax.text(
                0.5,
                0.5,
                "No historical data",
                ha="center",
                va="center",
                fontsize=12,
            )

            self.canvas.draw()
            return

        # Single snapshot

        if len(values) == 1:

            self.ax.scatter(
                labels,
                values,
                s=80,
            )

            self.ax.text(
                0.5,
                0.92,
                "Need at least 2 snapshots for trend",
                transform=self.ax.transAxes,
                ha="center",
                fontsize=9,
            )

        else:

            self.ax.plot(
                labels,
                values,
                marker="o",
                linewidth=2,
            )

        self.ax.tick_params(
            axis="x",
            rotation=20,
        )

        self.ax.grid(
            True,
            linestyle="--",
            alpha=0.35,
        )

        self.ax.set_title(self.title)

        # Auto format large numbers

        if values and max(abs(v) for v in values) > 1_00_00_000:

            self.ax.yaxis.set_major_formatter(
                FuncFormatter(
                    lambda x, pos: f"{x/1e7:.1f} Cr"
                )
            )

        elif values and max(abs(v) for v in values) > 1_00_000:

            self.ax.yaxis.set_major_formatter(
                FuncFormatter(
                    lambda x, pos: f"{x/1e5:.1f} L"
                )
            )

        self.figure.tight_layout()

        self.canvas.draw()

    # ---------------------------------------------------------

    def plot_dataframe(
        self,
        dataframe: pd.DataFrame,
        *,
        x_column: str,
        y_column: str,
    ) -> None:
        """
        Plot directly from a dataframe.
        """

        if dataframe.empty:

            self.plot([], [])
            return

        labels = (
            dataframe[x_column]
            .dt.strftime("%d-%b")
            .tolist()
        )

        values = dataframe[y_column].tolist()

        self.plot(
            labels,
            values,
        )