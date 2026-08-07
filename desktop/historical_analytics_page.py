"""
Finance Utility Suite
Enterprise RMS

Historical Analytics Dashboard

Version : 3.0.0
Author  : Shiva Kumar
"""

from __future__ import annotations

import customtkinter as ctk

from core.services.historical_analytics_service import (
    HistoricalAnalyticsService,
)

from desktop.widgets.history_summary_card import (
    HistorySummaryCard,
)

from desktop.widgets.historical_chart_widget import (
    HistoricalChartWidget,
)


class HistoricalAnalyticsPage(ctk.CTkFrame):
    """
    Historical Analytics Dashboard.

    Displays

    • Snapshot Summary
    • Exposure Trend
    • MTM Trend
    • Risk Trend
    • Client Trend
    • Symbol Trend
    """

    def __init__(self, parent):

        super().__init__(parent)

        self.service = HistoricalAnalyticsService()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()

        self._build_body()

        self.refresh()

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    def _build_header(self):

        header = ctk.CTkFrame(
            self,
            corner_radius=10,
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(15, 10),
        )

        title = ctk.CTkLabel(
            header,
            text="Historical Analytics",
            font=ctk.CTkFont(
                size=26,
                weight="bold",
            ),
        )

        title.pack(
            anchor="w",
            padx=20,
            pady=15,
        )

    # ---------------------------------------------------------
    # Body
    # ---------------------------------------------------------

    def _build_body(self):

        self.body = ctk.CTkFrame(self)

        self.body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 15),
        )

        self.body.grid_rowconfigure(
            1,
            weight=1,
        )

        self.body.grid_columnconfigure(
            0,
            weight=1,
        )

        self._build_summary_cards()

        self._build_charts()

    # ---------------------------------------------------------
    # Summary Cards
    # ---------------------------------------------------------

    def _build_summary_cards(self):

        cards = ctk.CTkFrame(self.body)

        cards.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=10,
        )

        for i in range(5):

            cards.grid_columnconfigure(
                i,
                weight=1,
            )

        self.snapshot_card = HistorySummaryCard(
            cards,
            "Snapshots",
            "--",
        )

        self.snapshot_card.grid(
            row=0,
            column=0,
            padx=6,
            pady=6,
            sticky="ew",
        )

        self.client_card = HistorySummaryCard(
            cards,
            "Clients",
            "--",
        )

        self.client_card.grid(
            row=0,
            column=1,
            padx=6,
            pady=6,
            sticky="ew",
        )

        self.symbol_card = HistorySummaryCard(
            cards,
            "Symbols",
            "--",
        )

        self.symbol_card.grid(
            row=0,
            column=2,
            padx=6,
            pady=6,
            sticky="ew",
        )

        self.exposure_card = HistorySummaryCard(
            cards,
            "Exposure",
            "--",
        )

        self.exposure_card.grid(
            row=0,
            column=3,
            padx=6,
            pady=6,
            sticky="ew",
        )

        self.mtm_card = HistorySummaryCard(
            cards,
            "MTM",
            "--",
        )

        self.mtm_card.grid(
            row=0,
            column=4,
            padx=6,
            pady=6,
            sticky="ew",
        )

    # ---------------------------------------------------------
    # Charts
    # ---------------------------------------------------------

    def _build_charts(self):

        charts = ctk.CTkScrollableFrame(
            self.body,
        )

        charts.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10),
        )

        charts.grid_columnconfigure(
            0,
            weight=1,
        )

        charts.grid_rowconfigure(
            0,
            weight=1,
        )

        charts.grid_rowconfigure(
            1,
            weight=1,
        )

        charts.grid_rowconfigure(
            2,
            weight=1,
        )

        charts.grid_rowconfigure(
            3,
            weight=1,
        )

        charts.grid_rowconfigure(
            4,
            weight=1,
        )

        self.exposure_chart = HistoricalChartWidget(
            charts,
            title="Exposure Trend",
        )

        self.exposure_chart.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=8,
        )

        self.mtm_chart = HistoricalChartWidget(
            charts,
            title="MTM Trend",
        )

        self.mtm_chart.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=8,
        )

        self.risk_chart = HistoricalChartWidget(
            charts,
            title="Risk Score Trend",
        )

        self.risk_chart.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=8,
        )

        self.client_chart = HistoricalChartWidget(
            charts,
            title="Client Trend",
        )

        self.client_chart.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=8,
        )

        self.symbol_chart = HistoricalChartWidget(
            charts,
            title="Symbol Trend",
        )

        self.symbol_chart.grid(
            row=4,
            column=0,
            sticky="ew",
            pady=(8, 20),
        )

            # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------

    def refresh(self):
        """
        Refresh dashboard.
        """

        self._refresh_cards()

        self._refresh_charts()

    # ---------------------------------------------------------
    # Cards
    # ---------------------------------------------------------

    def _refresh_cards(self):

        try:

            history = self.service.portfolio_history()

            summary = self.service.latest_summary()

            if history.empty or not summary:

                self.clear()

                return

            self.snapshot_card.update_value(
                str(len(history))
            )

            self.client_card.update_value(
                str(summary["clients"])
            )

            self.symbol_card.update_value(
                str(summary["symbols"])
            )

            self.exposure_card.update_value(
                self._format_currency(
                    summary["total_exposure"]
                )
            )

            self.mtm_card.update_value(
                self._format_currency(
                    summary["total_mtm"]
                )
            )

        except Exception as e:

            print(
                "Historical Card Error:",
                e,
            )

            self.clear()

    # ---------------------------------------------------------
    # Charts
    # ---------------------------------------------------------

    def _refresh_charts(self):

        try:

            self.exposure_chart.plot_dataframe(
                self.service.exposure_trend(),
                x_column="business_date",
                y_column="total_exposure",
            )

        except Exception as e:

            print(
                "Exposure Trend Error:",
                e,
            )

        try:

            self.mtm_chart.plot_dataframe(
                self.service.mtm_trend(),
                x_column="business_date",
                y_column="total_mtm",
            )

        except Exception as e:

            print(
                "MTM Trend Error:",
                e,
            )

        try:

            self.risk_chart.plot_dataframe(
                self.service.risk_score_trend(),
                x_column="business_date",
                y_column="risk_score",
            )

        except Exception as e:

            print(
                "Risk Trend Error:",
                e,
            )

        try:

            self.client_chart.plot_dataframe(
                self.service.client_trend(),
                x_column="business_date",
                y_column="clients",
            )

        except Exception as e:

            print(
                "Client Trend Error:",
                e,
            )

        try:

            self.symbol_chart.plot_dataframe(
                self.service.symbol_trend(),
                x_column="business_date",
                y_column="symbols",
            )

        except Exception as e:

            print(
                "Symbol Trend Error:",
                e,
            )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _format_currency(
        value: float,
    ) -> str:
        """
        Format values into
        Crores/Lakhs.
        """

        negative = value < 0

        value = abs(value)

        if value >= 1e7:

            text = f"₹{value/1e7:.2f} Cr"

        elif value >= 1e5:

            text = f"₹{value/1e5:.2f} L"

        else:

            text = f"₹{value:,.2f}"

        if negative:

            return "-" + text

        return text

    # ---------------------------------------------------------

    def clear(self):
        """
        Reset dashboard.
        """

        self.snapshot_card.update_value("--")

        self.client_card.update_value("--")

        self.symbol_card.update_value("--")

        self.exposure_card.update_value("--")

        self.mtm_card.update_value("--")

        self.exposure_chart.plot([], [])

        self.mtm_chart.plot([], [])

        self.risk_chart.plot([], [])

        self.client_chart.plot([], [])

        self.symbol_chart.plot([], [])