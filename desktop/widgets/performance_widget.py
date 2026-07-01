"""
Finance Utility Suite
Performance Widget

Displays portfolio performance statistics in a
professional dashboard panel.
"""

from __future__ import annotations

import customtkinter as ctk


class PerformanceWidget(ctk.CTkFrame):
    """
    Reusable performance summary widget.

    Example
    -------
    widget.update_metrics({
        "Best Performer": "TCS (+18.52%)",
        "Worst Performer": "ITC (-5.42%)",
        "Average Return": "8.32%",
        "Winning Stocks": "18",
        "Losing Stocks": "6",
        "Total Profit": "₹42,650"
    })
    """

    def __init__(self, master, title="Portfolio Performance"):

        super().__init__(master)

        self.metric_labels = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 16, "bold")
        )

        title_label.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(12, 18)
        )

        metrics = [
            "Best Performer",
            "Worst Performer",
            "Average Return",
            "Winning Stocks",
            "Losing Stocks",
            "Total Profit"
        ]

        for row, metric in enumerate(metrics, start=1):

            name = ctk.CTkLabel(
                self,
                text=metric,
                anchor="w",
                font=("Segoe UI", 12)
            )

            name.grid(
                row=row,
                column=0,
                sticky="w",
                padx=20,
                pady=6
            )

            value = ctk.CTkLabel(
                self,
                text="-",
                anchor="e",
                font=("Segoe UI", 12, "bold")
            )

            value.grid(
                row=row,
                column=1,
                sticky="e",
                padx=20,
                pady=6
            )

            self.metric_labels[metric] = value

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def update_metrics(self, metrics: dict):

        """
        Update displayed metrics.

        Parameters
        ----------
        metrics : dict

        Example
        -------
        {
            "Best Performer": "TCS (+12%)",
            "Worst Performer": "ITC (-4%)"
        }
        """

        for key, value in metrics.items():

            if key in self.metric_labels:
                self.metric_labels[key].configure(
                    text=str(value)
                )

    def clear(self):

        """Reset all values."""

        for label in self.metric_labels.values():
            label.configure(text="-")